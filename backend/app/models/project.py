import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ProjectField(str, enum.Enum):
    computer_science = "computer_science"
    engineering = "engineering"
    business = "business"
    health_sciences = "health_sciences"


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    in_progress = "in_progress"
    completed = "completed"


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    field: Mapped[ProjectField] = mapped_column(
        Enum(ProjectField, name="projectfield"), nullable=False
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="projectstatus"),
        default=ProjectStatus.draft,
        server_default="draft",
        nullable=False,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner: Mapped["User"] = relationship("User", back_populates="projects")
