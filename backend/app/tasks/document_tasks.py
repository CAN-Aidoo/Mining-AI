"""Celery tasks for AI document section generation."""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.config import get_settings
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, name="mining_ai.documents.generate_all_sections")
def generate_all_sections_task(
    self,
    document_id: str,
    project_title: str,
    field: str,
    owner_id: str,
) -> dict:
    """
    Celery task: generate every section of an AcademicDocument using Claude.
    Updates the document record in Postgres as each section completes.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy import select

    from app.models.document import AcademicDocument
    from app.models.paper import Paper
    from app.services.document import generate_section, build_references_section, SECTIONS_BY_FIELD

    async def _run() -> dict:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        doc_uuid = uuid.UUID(document_id)
        owner_uuid = uuid.UUID(owner_id)
        generated_count = 0
        errors = []

        async with async_session() as db:
            # Load document
            result = await db.execute(
                select(AcademicDocument).where(AcademicDocument.id == doc_uuid)
            )
            doc = result.scalar_one_or_none()
            if not doc:
                return {"error": f"Document {document_id} not found"}

            doc.status = "generating"
            await db.flush()
            await db.commit()

            # Load user's papers for context
            papers_result = await db.execute(
                select(Paper).where(Paper.owner_id == owner_uuid).limit(10)
            )
            papers = list(papers_result.scalars().all())

            # Determine sections for field
            sections_list = SECTIONS_BY_FIELD.get(field, SECTIONS_BY_FIELD["computer_science"])

            sections_data = dict(doc.sections) if doc.sections else {}

            for section_name in sections_list:
                if section_name == "references":
                    ref_text = build_references_section(papers, doc.citation_style)
                    sections_data["references"] = {
                        "content": ref_text,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                    }
                    generated_count += 1
                    continue
                try:
                    content = await generate_section(
                        document=doc,
                        section_name=section_name,
                        project_title=project_title,
                        field=field,
                        papers=papers,
                    )
                    sections_data[section_name] = {
                        "content": content,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                    }
                    generated_count += 1
                except Exception as exc:
                    logger.error("Section %s generation failed: %s", section_name, exc)
                    errors.append(f"{section_name}: {exc}")

            doc.sections = sections_data
            doc.status = "error" if errors else "complete"
            await db.commit()

        await engine.dispose()
        return {"generated": generated_count, "errors": errors}

    return asyncio.run(_run())
