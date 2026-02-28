"""
Research Library endpoints.

Routes:
    POST   /api/v1/research/papers/ingest   - Ingest papers from DOI/arXiv/query
    POST   /api/v1/research/papers/search   - Semantic search over indexed papers
    GET    /api/v1/research/papers          - List user's indexed papers
    GET    /api/v1/research/papers/{id}     - Get a specific paper
    DELETE /api/v1/research/papers/{id}     - Delete a paper from the library
    POST   /api/v1/research/bulk-ingest     - Trigger Celery bulk-ingest task
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.paper import Paper
from app.models.user import User
from app.schemas.research import (
    PaperIngest,
    PaperListResponse,
    PaperResponse,
    SearchRequest,
    SearchResult,
)
from app.services import chroma as chroma_svc
from app.services import research as research_svc

router = APIRouter()


@router.post("/papers/ingest", response_model=list[PaperResponse], status_code=201)
async def ingest_papers(
    payload: PaperIngest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[Paper]:
    """
    Ingest papers into the user's research library.
    Accepts a DOI, an arXiv ID, or a free-text query (fetches from Semantic Scholar + arXiv).
    """
    papers: list[Paper] = []

    if payload.doi:
        data = await research_svc.fetch_by_doi(payload.doi)
        if not data:
            raise HTTPException(status_code=404, detail=f"Paper with DOI '{payload.doi}' not found")
        papers.append(await research_svc.save_paper(db, data, current_user.id))

    elif payload.arxiv_id:
        data = await research_svc.fetch_arxiv(payload.arxiv_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"arXiv paper '{payload.arxiv_id}' not found")
        papers.append(await research_svc.save_paper(db, data, current_user.id))

    elif payload.query:
        limit = min(payload.limit, 10)
        ss_results = await research_svc.search_semantic_scholar(payload.query, limit=limit)
        ax_results = await research_svc.search_arxiv(payload.query, limit=limit)
        for pdata in ss_results + ax_results:
            paper = await research_svc.save_paper(db, pdata, current_user.id)
            papers.append(paper)
    else:
        raise HTTPException(status_code=422, detail="Provide doi, arxiv_id, or query")

    return papers


@router.post("/papers/search", response_model=list[SearchResult])
async def search_papers(
    payload: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[SearchResult]:
    """Semantic search over the user's indexed paper library."""
    results = await research_svc.semantic_search(
        query=payload.query,
        db=db,
        owner_id=current_user.id,
        limit=payload.limit,
    )
    return [SearchResult(paper=PaperResponse.model_validate(p), score=score) for p, score in results]


@router.get("/papers", response_model=PaperListResponse)
async def list_papers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PaperListResponse:
    """List all papers in the user's research library."""
    rows = await db.execute(
        select(Paper)
        .where(Paper.owner_id == current_user.id)
        .order_by(Paper.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    papers = list(rows.scalars().all())
    count = await db.execute(
        select(func.count()).select_from(Paper).where(Paper.owner_id == current_user.id)
    )
    return PaperListResponse(items=papers, total=count.scalar_one())


@router.get("/papers/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Paper:
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.owner_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.delete("/papers/{paper_id}", status_code=204)
async def delete_paper(
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.owner_id == current_user.id)
    )
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    if paper.chroma_id:
        chroma_svc.delete_paper(paper.chroma_id)
    await db.delete(paper)
    return Response(status_code=204)


@router.post("/bulk-ingest", status_code=202)
async def bulk_ingest(
    queries: list[str],
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Trigger a Celery task to bulk-ingest papers for a list of queries."""
    from app.tasks.research_tasks import bulk_ingest_task
    task = bulk_ingest_task.delay(queries, str(current_user.id))
    return {"task_id": task.id, "status": "queued", "queries": queries}
