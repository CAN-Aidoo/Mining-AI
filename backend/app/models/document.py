import uuid

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class AcademicDocument(UUIDMixin, TimestampMixin, Base):
    """AI-generated academic document tied to a project."""

    __tablename__ = "academic_documents"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    # 'apa' or 'ieee'
    citation_style: Mapped[str] = mapped_column(
        String(10), nullable=False, default="apa", server_default="apa"
    )
    # 'draft' | 'generating' | 'complete' | 'error'
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", server_default="draft"
    )
    # {section_name: {content: str, generated_at: str}}
    sections: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
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
