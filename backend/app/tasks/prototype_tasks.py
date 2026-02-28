"""Celery tasks for AI prototype code generation."""

import asyncio
import logging
import uuid

from app.config import get_settings
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, name="mining_ai.prototypes.build")
def build_prototype_task(self, prototype_id: str) -> dict:
    """
    Celery task: generate Gradio prototype code using Claude.
    Updates prototype record with generated code and status.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy import select

    from app.models.prototype import Prototype
    from app.services.prototype import generate_prototype_code

    async def _run() -> dict:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        proto_uuid = uuid.UUID(prototype_id)

        async with async_session() as db:
            result = await db.execute(
                select(Prototype).where(Prototype.id == proto_uuid)
            )
            proto = result.scalar_one_or_none()
            if not proto:
                return {"error": f"Prototype {prototype_id} not found"}

            proto.status = "building"
            proto.build_log = "Starting code generation…"
            await db.commit()

            try:
                code, requirements = await generate_prototype_code(proto)
                proto.generated_code = code
                proto.requirements_txt = requirements
                proto.status = "ready"
                proto.build_log = "Build completed successfully."
            except Exception as exc:
                logger.error("Prototype build failed (%s): %s", prototype_id, exc)
                proto.status = "error"
                proto.build_log = f"Build failed: {exc}"

            await db.commit()

        await engine.dispose()
        return {"status": proto.status}

    return asyncio.run(_run())
