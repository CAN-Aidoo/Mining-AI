"""
Mining AI Platform - Documents Endpoints (Week 1 Stub).

Routes:
    GET    /api/v1/documents/              - List documents
    POST   /api/v1/documents/upload        - Upload and process document
    GET    /api/v1/documents/{id}          - Get document by ID
    DELETE /api/v1/documents/{id}          - Delete document
    GET    /api/v1/documents/{id}/chunks   - Get document chunks
    POST   /api/v1/documents/{id}/generate - Generate section content
"""

import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/", summary="List documents")
async def list_documents() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 4"},
    )


@router.post("/upload", summary="Upload document")
async def upload_document() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 4"},
    )


@router.get("/{document_id}", summary="Get document")
async def get_document(document_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 4"},
    )


@router.delete("/{document_id}", summary="Delete document")
async def delete_document(document_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 4"},
    )


@router.get("/{document_id}/chunks", summary="Get document chunks")
async def get_document_chunks(document_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 4"},
    )


@router.post("/{document_id}/generate", summary="Generate section content")
async def generate_section(document_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 4"},
    )
