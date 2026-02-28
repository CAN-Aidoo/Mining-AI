"""
Prototype Builder endpoints.

Routes:
    GET    /api/v1/prototypes/                  - List user's prototypes
    POST   /api/v1/prototypes/                  - Create prototype spec
    GET    /api/v1/prototypes/{id}              - Get prototype
    PATCH  /api/v1/prototypes/{id}              - Update prototype spec
    DELETE /api/v1/prototypes/{id}              - Delete prototype
    POST   /api/v1/prototypes/{id}/build        - Trigger Celery build task
    GET    /api/v1/prototypes/{id}/status       - Get build status
    GET    /api/v1/prototypes/{id}/download     - Download generated code as .zip
"""

import io
import uuid
import zipfile

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.project import Project
from app.models.prototype import Prototype
from app.models.user import User
from app.schemas.prototype import (
    BuildStatusResponse,
    PrototypeCreate,
    PrototypeListResponse,
    PrototypeResponse,
    PrototypeUpdate,
    PROTOTYPE_TYPES,
)

router = APIRouter()


async def _get_owned_prototype(
    prototype_id: uuid.UUID, db: AsyncSession, current_user: User
) -> Prototype:
    result = await db.execute(
        select(Prototype).where(
            Prototype.id == prototype_id,
            Prototype.owner_id == current_user.id,
        )
    )
    proto = result.scalar_one_or_none()
    if not proto:
        raise HTTPException(status_code=404, detail="Prototype not found")
    return proto


@router.get("/", response_model=PrototypeListResponse)
async def list_prototypes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PrototypeListResponse:
    rows = await db.execute(
        select(Prototype)
        .where(Prototype.owner_id == current_user.id)
        .order_by(Prototype.created_at.desc())
    )
    items = list(rows.scalars().all())
    count = await db.execute(
        select(func.count()).select_from(Prototype).where(Prototype.owner_id == current_user.id)
    )
    return PrototypeListResponse(items=items, total=count.scalar_one())


@router.post("/", response_model=PrototypeResponse, status_code=201)
async def create_prototype(
    payload: PrototypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Prototype:
    if payload.prototype_type not in PROTOTYPE_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"prototype_type must be one of {PROTOTYPE_TYPES}",
        )
    proj_result = await db.execute(
        select(Project).where(
            Project.id == payload.project_id,
            Project.owner_id == current_user.id,
        )
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    proto = Prototype(
        title=payload.title,
        prototype_type=payload.prototype_type,
        description=payload.description,
        input_description=payload.input_description,
        project_id=payload.project_id,
        owner_id=current_user.id,
    )
    db.add(proto)
    await db.flush()
    return proto


@router.get("/{prototype_id}", response_model=PrototypeResponse)
async def get_prototype(
    prototype_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Prototype:
    return await _get_owned_prototype(prototype_id, db, current_user)


@router.patch("/{prototype_id}", response_model=PrototypeResponse)
async def update_prototype(
    prototype_id: uuid.UUID,
    payload: PrototypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Prototype:
    proto = await _get_owned_prototype(prototype_id, db, current_user)
    if proto.status == "building":
        raise HTTPException(status_code=409, detail="Cannot update while building")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(proto, field, value)
    await db.flush()
    return proto


@router.delete("/{prototype_id}", status_code=204)
async def delete_prototype(
    prototype_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    proto = await _get_owned_prototype(prototype_id, db, current_user)
    await db.delete(proto)
    return Response(status_code=204)


@router.post("/{prototype_id}/build", status_code=202)
async def build_prototype(
    prototype_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Trigger a Celery task to generate the prototype code using Claude."""
    proto = await _get_owned_prototype(prototype_id, db, current_user)
    if proto.status == "building":
        raise HTTPException(status_code=409, detail="Build already in progress")

    from app.tasks.prototype_tasks import build_prototype_task
    task = build_prototype_task.delay(str(prototype_id))

    proto.status = "building"
    proto.celery_task_id = task.id
    proto.build_log = "Build queued…"
    await db.flush()
    return {"task_id": task.id, "status": "queued", "prototype_id": str(prototype_id)}


@router.get("/{prototype_id}/status", response_model=BuildStatusResponse)
async def get_build_status(
    prototype_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BuildStatusResponse:
    proto = await _get_owned_prototype(prototype_id, db, current_user)
    return BuildStatusResponse(
        prototype_id=proto.id,
        status=proto.status,
        celery_task_id=proto.celery_task_id,
        build_log=proto.build_log,
    )


@router.get("/{prototype_id}/download")
async def download_prototype(
    prototype_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """Download the generated prototype as a .zip containing app.py + requirements.txt."""
    proto = await _get_owned_prototype(prototype_id, db, current_user)
    if proto.status != "ready" or not proto.generated_code:
        raise HTTPException(
            status_code=409,
            detail="Prototype code not ready. Build it first.",
        )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("app.py", proto.generated_code)
        zf.writestr("requirements.txt", proto.requirements_txt or "gradio>=4.0.0\n")
        readme = (
            f"# {proto.title}\n\n"
            f"Type: {proto.prototype_type}\n\n"
            f"## Setup\n\n"
            f"```bash\npip install -r requirements.txt\npython app.py\n```\n"
        )
        zf.writestr("README.md", readme)
    buf.seek(0)

    safe_title = "".join(c for c in proto.title if c.isalnum() or c in " _-")[:40]
    filename = f"{safe_title}_{proto.prototype_type}.zip"

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
