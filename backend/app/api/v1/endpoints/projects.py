"""
Mining AI Platform - Projects Endpoints (Week 1 Stub).

Routes:
    GET    /api/v1/projects/       - List projects
    POST   /api/v1/projects/       - Create project
    GET    /api/v1/projects/{id}   - Get project by ID
    PUT    /api/v1/projects/{id}   - Update project
    DELETE /api/v1/projects/{id}   - Delete project
"""

import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/", summary="List projects")
async def list_projects() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )


@router.post("/", summary="Create project")
async def create_project() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )


@router.get("/{project_id}", summary="Get project")
async def get_project(project_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )


@router.put("/{project_id}", summary="Update project")
async def update_project(project_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )


@router.delete("/{project_id}", summary="Delete project")
async def delete_project(project_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )
