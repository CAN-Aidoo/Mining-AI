import uuid

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Paper(UUIDMixin, TimestampMixin, Base):
    """Indexed academic paper stored per-user."""

    __tablename__ = "papers"

    title: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    field_tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    citations_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    chroma_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
