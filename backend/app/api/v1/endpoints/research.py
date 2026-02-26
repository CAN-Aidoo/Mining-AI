"""
Mining AI Platform - Research Endpoints (Week 1 Stub).

Routes:
    GET    /api/v1/research/          - List research sessions
    POST   /api/v1/research/          - Create new research session
    GET    /api/v1/research/{id}      - Get research session by ID
    DELETE /api/v1/research/{id}      - Delete research session
    POST   /api/v1/research/{id}/run  - Trigger research agent run
"""

import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/", summary="List research sessions")
async def list_research() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 3"},
    )


@router.post("/", summary="Create research session")
async def create_research() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 3"},
    )


@router.get("/{research_id}", summary="Get research session")
async def get_research(research_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 3"},
    )


@router.delete("/{research_id}", summary="Delete research session")
async def delete_research(research_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 3"},
    )


@router.post("/{research_id}/run", summary="Run research agent")
async def run_research(research_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 3"},
    )
