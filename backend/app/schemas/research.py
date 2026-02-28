import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class PaperIngest(BaseModel):
    """Ingest a paper by DOI, arXiv ID, or search query."""
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    query: Optional[str] = None  # search Semantic Scholar
    limit: int = 5  # papers to fetch per search query


class PaperResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    abstract: Optional[str]
    authors: list[str]
    year: Optional[int]
    doi: Optional[str]
    url: Optional[str]
    source: str
    field_tags: list[str]
    citations_count: int
    owner_id: uuid.UUID
    created_at: datetime


class PaperListResponse(BaseModel):
    items: list[PaperResponse]
    total: int


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    field_filter: Optional[str] = None


class SearchResult(BaseModel):
    paper: PaperResponse
    score: float  # relevance score 0-1
