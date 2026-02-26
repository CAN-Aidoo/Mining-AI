"""
Mining AI Platform - SQLAlchemy Declarative Base.

All ORM models in the project inherit from Base defined here.
This allows Alembic autogenerate to detect all tables.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Shared declarative base.
    All models inherit from this class.
    """
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at columns to any model.

    Usage:
        class MyModel(TimestampMixin, Base):
            __tablename__ = "my_models"
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDMixin:
    """
    Adds a UUID primary key to any model.

    Usage:
        class MyModel(UUIDMixin, TimestampMixin, Base):
            __tablename__ = "my_models"
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
