import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.project import ProjectField, ProjectStatus


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    field: ProjectField


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    field: Optional[ProjectField] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    description: Optional[str]
    field: ProjectField
    status: ProjectStatus
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
