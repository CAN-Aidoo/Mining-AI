import uuid

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Prototype(UUIDMixin, TimestampMixin, Base):
    """AI-generated software prototype for a project."""

    __tablename__ = "prototypes"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    # 'classifier' | 'recommender' | 'chatbot' | 'text_tool' | 'dashboard'
    prototype_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    input_description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 'draft' | 'building' | 'ready' | 'error'
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", server_default="draft"
    )
    generated_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements_txt: Mapped[str | None] = mapped_column(Text, nullable=True)
    build_log: Mapped[str | None] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
