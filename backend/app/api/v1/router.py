"""
Mining AI Platform - API v1 Router Aggregator.

Imports and includes all endpoint routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    documents,
    projects,
    prototypes,
    research,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(prototypes.router, prefix="/prototypes", tags=["prototypes"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
