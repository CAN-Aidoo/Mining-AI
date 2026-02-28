"""
ChromaDB service — manages vector storage for research papers.

Uses OpenAI text-embedding-3-small when OPENAI_API_KEY is set.
Falls back to ChromaDB's built-in embedding function otherwise.
"""

import logging
from typing import Any, Optional

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_embedding_function() -> Any:
    """Return OpenAI embedding function if API key available, else None (uses default)."""
    if settings.OPENAI_API_KEY:
        return OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.EMBEDDING_MODEL,
        )
    logger.warning(
        "OPENAI_API_KEY not set — ChromaDB will use its default embedding function. "
        "Semantic search quality may be reduced."
    )
    return None


def get_chroma_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )


def get_papers_collection() -> chromadb.Collection:
    client = get_chroma_client()
    ef = _get_embedding_function()
    kwargs: dict[str, Any] = {"name": settings.CHROMA_COLLECTION_RESEARCH}
    if ef:
        kwargs["embedding_function"] = ef
    return client.get_or_create_collection(**kwargs)


def upsert_paper(
    chroma_id: str,
    title: str,
    abstract: str,
    metadata: dict,
) -> None:
    """Store or update a paper embedding in ChromaDB."""
    try:
        collection = get_papers_collection()
        document_text = f"{title}\n\n{abstract or ''}"
        collection.upsert(
            ids=[chroma_id],
            documents=[document_text],
            metadatas=[metadata],
        )
    except Exception as exc:
        logger.error("ChromaDB upsert failed for %s: %s", chroma_id, exc)


def search_papers(
    query: str,
    n_results: int = 10,
    where: Optional[dict] = None,
) -> list[dict]:
    """
    Semantic search over indexed papers.
    Returns list of {id, distance, metadata} dicts.
    """
    try:
        collection = get_papers_collection()
        kwargs: dict[str, Any] = {
            "query_texts": [query],
            "n_results": min(n_results, collection.count() or 1),
        }
        if where:
            kwargs["where"] = where
        results = collection.query(**kwargs)
        output = []
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        for chroma_id, dist, meta in zip(ids, distances, metadatas):
            output.append(
                {"chroma_id": chroma_id, "distance": dist, "metadata": meta or {}}
            )
        return output
    except Exception as exc:
        logger.error("ChromaDB search failed: %s", exc)
        return []


def delete_paper(chroma_id: str) -> None:
    try:
        collection = get_papers_collection()
        collection.delete(ids=[chroma_id])
    except Exception as exc:
        logger.error("ChromaDB delete failed for %s: %s", chroma_id, exc)
