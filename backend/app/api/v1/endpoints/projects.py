"""
Mining AI Platform - Projects Endpoints.

Routes:
    GET    /api/v1/projects/           - List current user's projects
    POST   /api/v1/projects/           - Create a new project
    GET    /api/v1/projects/{id}       - Get a project by ID
    PATCH  /api/v1/projects/{id}       - Partially update a project
    DELETE /api/v1/projects/{id}       - Delete a project
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter()


async def _get_owned_project(
    project_id: uuid.UUID, db: AsyncSession, current_user: User
) -> Project:
    """Return the project if it exists and belongs to current_user, else 404."""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id, Project.owner_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectListResponse:
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
    )
    items = list(result.scalars().all())
    count_result = await db.execute(
        select(func.count()).select_from(Project).where(Project.owner_id == current_user.id)
    )
    return ProjectListResponse(items=items, total=count_result.scalar_one())


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Project:
    project = Project(**payload.model_dump(), owner_id=current_user.id)
    db.add(project)
    await db.flush()
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Project:
    return await _get_owned_project(project_id, db, current_user)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Project:
    project = await _get_owned_project(project_id, db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.flush()
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    project = await _get_owned_project(project_id, db, current_user)
    await db.delete(project)
    return Response(status_code=204)
