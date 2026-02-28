"""Celery tasks for bulk research paper ingestion."""

import asyncio
import logging
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.paper import Paper
from app.services import chroma as chroma_svc
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, name="mining_ai.research.bulk_ingest")
def bulk_ingest_task(self, queries: list[str], owner_id: str, limit_per_query: int = 5) -> dict:
    """
    Celery task: run multiple Semantic Scholar + arXiv searches,
    persist results, and index in ChromaDB.

    Runs inside the Celery worker (sync context using asyncio.run).
    """
    from app.services.research import search_semantic_scholar, search_arxiv, save_paper
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    ingested = 0
    errors = []

    async def _run():
        nonlocal ingested
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        uid = uuid.UUID(owner_id)
        async with async_session() as db:
            for query in queries:
                for source_fn in [search_semantic_scholar, search_arxiv]:
                    try:
                        papers_data = await source_fn(query, limit=limit_per_query)
                        for pdata in papers_data:
                            await save_paper(db, pdata, uid)
                            ingested += 1
                    except Exception as exc:
                        errors.append(str(exc))
            await db.commit()
        await engine.dispose()

    asyncio.run(_run())
    return {"ingested": ingested, "errors": errors}
