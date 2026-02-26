"""
Mining AI Platform - Prototypes Endpoints (Week 1 Stub).

Routes:
    GET    /api/v1/prototypes/              - List prototypes
    POST   /api/v1/prototypes/              - Create prototype
    GET    /api/v1/prototypes/{id}          - Get prototype by ID
    PUT    /api/v1/prototypes/{id}          - Update prototype
    DELETE /api/v1/prototypes/{id}          - Delete prototype
    POST   /api/v1/prototypes/{id}/build    - Trigger prototype build
    GET    /api/v1/prototypes/{id}/status   - Get build status
"""

import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/", summary="List prototypes")
async def list_prototypes() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 5"},
    )


@router.post("/", summary="Create prototype")
async def create_prototype() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 5"},
    )


@router.get("/{prototype_id}", summary="Get prototype")
async def get_prototype(prototype_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 5"},
    )


@router.put("/{prototype_id}", summary="Update prototype")
async def update_prototype(prototype_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 5"},
    )


@router.delete("/{prototype_id}", summary="Delete prototype")
async def delete_prototype(prototype_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 5"},
    )


@router.post("/{prototype_id}/build", summary="Build prototype")
async def build_prototype(prototype_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 5"},
    )


@router.get("/{prototype_id}/status", summary="Build status")
async def get_build_status(prototype_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 5"},
    )
