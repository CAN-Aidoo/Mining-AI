"""
Documentation Engine endpoints.

Routes:
    GET    /api/v1/documents/                        - List user's documents
    POST   /api/v1/documents/                        - Create a new document
    GET    /api/v1/documents/{id}                    - Get document with sections
    PATCH  /api/v1/documents/{id}                    - Update document metadata
    DELETE /api/v1/documents/{id}                    - Delete document
    POST   /api/v1/documents/{id}/generate           - Generate ALL sections (Celery)
    POST   /api/v1/documents/{id}/generate/{section} - Generate ONE section (sync)
    GET    /api/v1/documents/{id}/export             - Download as DOCX
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.document import AcademicDocument
from app.models.paper import Paper
from app.models.project import Project
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
    SectionGenerateRequest,
)
from app.services import document as doc_svc

router = APIRouter()


async def _get_owned_document(
    document_id: uuid.UUID, db: AsyncSession, current_user: User
) -> AcademicDocument:
    result = await db.execute(
        select(AcademicDocument).where(
            AcademicDocument.id == document_id,
            AcademicDocument.owner_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    project_id: Optional[uuid.UUID] = Query(None),
) -> DocumentListResponse:
    query = select(AcademicDocument).where(AcademicDocument.owner_id == current_user.id)
    if project_id:
        query = query.where(AcademicDocument.project_id == project_id)
    query = query.order_by(AcademicDocument.created_at.desc())
    rows = await db.execute(query)
    docs = list(rows.scalars().all())
    count_q = select(func.count()).select_from(AcademicDocument).where(
        AcademicDocument.owner_id == current_user.id
    )
    count = await db.execute(count_q)
    return DocumentListResponse(items=docs, total=count.scalar_one())


@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
    payload: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AcademicDocument:
    proj_result = await db.execute(
        select(Project).where(
            Project.id == payload.project_id,
            Project.owner_id == current_user.id,
        )
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    doc = AcademicDocument(
        title=payload.title,
        citation_style=payload.citation_style,
        project_id=payload.project_id,
        owner_id=current_user.id,
        sections={},
    )
    db.add(doc)
    await db.flush()
    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AcademicDocument:
    return await _get_owned_document(document_id, db, current_user)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    payload: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AcademicDocument:
    doc = await _get_owned_document(document_id, db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    await db.flush()
    return doc


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    doc = await _get_owned_document(document_id, db, current_user)
    await db.delete(doc)
    return Response(status_code=204)


@router.post("/{document_id}/generate", status_code=202)
async def generate_all_sections(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Trigger Celery task to generate ALL sections using Claude."""
    doc = await _get_owned_document(document_id, db, current_user)
    proj_result = await db.execute(
        select(Project).where(Project.id == doc.project_id)
    )
    project = proj_result.scalar_one_or_none()
    field = project.field.value if project else "computer_science"

    from app.tasks.document_tasks import generate_all_sections_task
    task = generate_all_sections_task.delay(
        document_id=str(document_id),
        project_title=doc.title,
        field=field,
        owner_id=str(current_user.id),
    )
    doc.status = "generating"
    await db.flush()
    return {"task_id": task.id, "status": "queued", "document_id": str(document_id)}


@router.post("/{document_id}/generate/{section_name}", response_model=DocumentResponse)
async def generate_one_section(
    document_id: uuid.UUID,
    section_name: str,
    payload: SectionGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AcademicDocument:
    """Synchronously generate a single section using Claude."""
    doc = await _get_owned_document(document_id, db, current_user)
    proj_result = await db.execute(
        select(Project).where(Project.id == doc.project_id)
    )
    project = proj_result.scalar_one_or_none()
    field = project.field.value if project else "computer_science"

    papers_result = await db.execute(
        select(Paper).where(Paper.owner_id == current_user.id).limit(8)
    )
    papers = list(papers_result.scalars().all())

    if section_name == "references":
        content = doc_svc.build_references_section(papers, doc.citation_style)
    else:
        content = await doc_svc.generate_section(
            document=doc,
            section_name=section_name,
            project_title=doc.title,
            field=field,
            papers=papers,
            extra_context=payload.extra_context,
        )

    sections = dict(doc.sections) if doc.sections else {}
    sections[section_name] = {
        "content": content,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    doc.sections = sections
    await db.flush()
    return doc


@router.get("/{document_id}/export")
async def export_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """Download the document as a formatted DOCX file."""
    doc = await _get_owned_document(document_id, db, current_user)
    papers_result = await db.execute(
        select(Paper).where(Paper.owner_id == current_user.id).limit(20)
    )
    papers = list(papers_result.scalars().all())
    docx_bytes = doc_svc.export_to_docx(doc, papers)
    safe_title = "".join(c for c in doc.title if c.isalnum() or c in " _-")[:60]
    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}.docx"'},
    )
