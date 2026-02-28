"""
Research service — fetches papers from Semantic Scholar & arXiv,
stores them in PostgreSQL, and indexes them in ChromaDB.
"""

import logging
import uuid
import xml.etree.ElementTree as ET
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.paper import Paper
from app.services import chroma as chroma_svc

logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
ARXIV_BASE = "https://export.arxiv.org/api/query"
ARXIV_NS = "http://www.w3.org/2005/Atom"

_FIELDS = "title,abstract,authors,year,externalIds,url,citationCount,fieldsOfStudy"


# ---------------------------------------------------------------------------
# External API helpers
# ---------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
async def _ss_get(path: str, params: dict) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"{SEMANTIC_SCHOLAR_BASE}{path}", params=params)
        resp.raise_for_status()
        return resp.json()


async def fetch_by_doi(doi: str) -> Optional[dict]:
    """Fetch paper details from Semantic Scholar by DOI."""
    try:
        data = await _ss_get(f"/paper/DOI:{doi}", {"fields": _FIELDS})
        return _parse_ss_paper(data)
    except Exception as exc:
        logger.warning("Semantic Scholar DOI lookup failed (%s): %s", doi, exc)
        return None


async def search_semantic_scholar(query: str, limit: int = 5) -> list[dict]:
    """Search Semantic Scholar for papers matching query."""
    try:
        data = await _ss_get(
            "/paper/search",
            {"query": query, "limit": limit, "fields": _FIELDS},
        )
        return [_parse_ss_paper(p) for p in data.get("data", [])]
    except Exception as exc:
        logger.warning("Semantic Scholar search failed (%s): %s", query, exc)
        return []


async def fetch_arxiv(arxiv_id: str) -> Optional[dict]:
    """Fetch paper from arXiv by ID (e.g. '2301.00001' or 'cs.AI/0001001')."""
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(ARXIV_BASE, params={"id_list": arxiv_id})
            resp.raise_for_status()
        return _parse_arxiv_xml(resp.text, limit=1)[0] if resp.text else None
    except Exception as exc:
        logger.warning("arXiv fetch failed (%s): %s", arxiv_id, exc)
        return None


async def search_arxiv(query: str, limit: int = 5) -> list[dict]:
    """Search arXiv for papers matching query."""
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                ARXIV_BASE,
                params={
                    "search_query": f"all:{query}",
                    "max_results": limit,
                    "sortBy": "relevance",
                },
            )
            resp.raise_for_status()
        return _parse_arxiv_xml(resp.text, limit=limit)
    except Exception as exc:
        logger.warning("arXiv search failed (%s): %s", query, exc)
        return []


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_ss_paper(data: dict) -> dict:
    authors = [a.get("name", "") for a in data.get("authors", [])]
    ext_ids = data.get("externalIds", {}) or {}
    doi = ext_ids.get("DOI")
    arxiv_id = ext_ids.get("ArXiv")
    url = data.get("url") or (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None)
    return {
        "title": data.get("title", "Untitled"),
        "abstract": data.get("abstract"),
        "authors": authors,
        "year": data.get("year"),
        "doi": doi,
        "url": url,
        "source": "semantic_scholar",
        "field_tags": data.get("fieldsOfStudy") or [],
        "citations_count": data.get("citationCount", 0),
    }


def _parse_arxiv_xml(xml_text: str, limit: int = 10) -> list[dict]:
    papers = []
    try:
        root = ET.fromstring(xml_text)
        for entry in root.findall(f"{{{ARXIV_NS}}}entry")[:limit]:
            title_el = entry.find(f"{{{ARXIV_NS}}}title")
            summary_el = entry.find(f"{{{ARXIV_NS}}}summary")
            published_el = entry.find(f"{{{ARXIV_NS}}}published")
            id_el = entry.find(f"{{{ARXIV_NS}}}id")
            title = title_el.text.strip() if title_el is not None else "Untitled"
            abstract = summary_el.text.strip() if summary_el is not None else None
            year = int(published_el.text[:4]) if published_el is not None else None
            url = id_el.text.strip() if id_el is not None else None
            authors = [
                a.find(f"{{{ARXIV_NS}}}name").text
                for a in entry.findall(f"{{{ARXIV_NS}}}author")
                if a.find(f"{{{ARXIV_NS}}}name") is not None
            ]
            papers.append({
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "year": year,
                "doi": None,
                "url": url,
                "source": "arxiv",
                "field_tags": ["computer_science"],
                "citations_count": 0,
            })
    except ET.ParseError as exc:
        logger.warning("arXiv XML parse error: %s", exc)
    return papers


# ---------------------------------------------------------------------------
# DB operations
# ---------------------------------------------------------------------------

async def save_paper(db: AsyncSession, paper_data: dict, owner_id: uuid.UUID) -> Paper:
    """Persist a paper to PostgreSQL (skip duplicates by DOI) and index in ChromaDB."""
    # Dedup by DOI if present
    doi = paper_data.get("doi")
    if doi:
        existing = await db.execute(
            select(Paper).where(Paper.doi == doi, Paper.owner_id == owner_id)
        )
        existing_paper = existing.scalar_one_or_none()
        if existing_paper:
            return existing_paper

    paper = Paper(
        owner_id=owner_id,
        **{k: v for k, v in paper_data.items()},
    )
    db.add(paper)
    await db.flush()

    # Index in ChromaDB
    chroma_id = str(paper.id)
    chroma_svc.upsert_paper(
        chroma_id=chroma_id,
        title=paper.title,
        abstract=paper.abstract or "",
        metadata={
            "paper_id": str(paper.id),
            "owner_id": str(owner_id),
            "year": paper.year or 0,
            "source": paper.source,
        },
    )
    paper.chroma_id = chroma_id
    await db.flush()
    return paper


async def semantic_search(
    query: str,
    db: AsyncSession,
    owner_id: uuid.UUID,
    limit: int = 10,
) -> list[tuple[Paper, float]]:
    """
    Semantic search via ChromaDB, resolve IDs to Paper records.
    Falls back to PostgreSQL ILIKE keyword search if ChromaDB returns nothing.
    """
    results = chroma_svc.search_papers(query, n_results=limit)

    if results:
        paper_ids = []
        scores = {}
        for r in results:
            pid = r["metadata"].get("paper_id")
            if pid:
                paper_ids.append(uuid.UUID(pid))
                # Convert distance to score (lower distance = higher score)
                dist = r.get("distance", 1.0)
                scores[pid] = max(0.0, 1.0 - dist)

        if paper_ids:
            rows = await db.execute(
                select(Paper).where(
                    Paper.id.in_(paper_ids),
                    Paper.owner_id == owner_id,
                )
            )
            papers = rows.scalars().all()
            return [(p, scores.get(str(p.id), 0.5)) for p in papers]

    # Keyword fallback
    rows = await db.execute(
        select(Paper)
        .where(
            Paper.owner_id == owner_id,
            Paper.title.ilike(f"%{query}%"),
        )
        .limit(limit)
    )
    return [(p, 0.5) for p in rows.scalars().all()]
