import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


PROTOTYPE_TYPES = ["classifier", "recommender", "chatbot", "text_tool", "dashboard"]


class PrototypeCreate(BaseModel):
    title: str
    prototype_type: str  # one of PROTOTYPE_TYPES
    description: str
    input_description: str  # describe what data / inputs the prototype uses
    project_id: uuid.UUID


class PrototypeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    input_description: Optional[str] = None


class PrototypeResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    prototype_type: str
    description: str
    input_description: str
    status: str
    generated_code: Optional[str]
    requirements_txt: Optional[str]
    build_log: Optional[str]
    celery_task_id: Optional[str]
    project_id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PrototypeListResponse(BaseModel):
    items: list[PrototypeResponse]
    total: int


class BuildStatusResponse(BaseModel):
    prototype_id: uuid.UUID
    status: str
    celery_task_id: Optional[str]
    build_log: Optional[str]
