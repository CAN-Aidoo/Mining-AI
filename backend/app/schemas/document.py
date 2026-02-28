import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str
    project_id: uuid.UUID
    citation_style: str = "apa"  # 'apa' or 'ieee'


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    citation_style: Optional[str] = None


class SectionGenerateRequest(BaseModel):
    """Request to generate a specific section using AI."""
    section_name: str
    extra_context: Optional[str] = None  # optional user notes for the section


class DocumentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    citation_style: str
    status: str
    sections: dict
    project_id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class SectionInfo(BaseModel):
    """Info about available sections for a project field."""
    field: str
    sections: list[str]
