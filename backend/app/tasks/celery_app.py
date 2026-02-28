"""
Mining AI Platform - Celery Application Instance.

Configures the Celery app with Redis broker and result backend.
All task modules must be listed in `include` so Celery discovers them.
"""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "mining_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.research_tasks",
        "app.tasks.document_tasks",
        "app.tasks.prototype_tasks",
    ],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task behavior
    task_track_started=True,
    task_acks_late=True,          # Re-queue task if worker crashes mid-execution
    worker_prefetch_multiplier=1,  # Fair task distribution
    # Result expiry (24 hours)
    result_expires=86400,
    # Retry defaults
    task_default_retry_delay=60,
    task_max_retries=3,
    # Beat schedule (add periodic tasks here in later weeks)
    beat_schedule={},
)


@celery_app.task(bind=True, name="mining_ai.health_check")
def health_check_task(self) -> dict:
    """Simple task to verify Celery worker is operational."""
    return {"status": "healthy", "worker_id": self.request.id}
