"""
Mining AI Platform - Auth Endpoints.

Routes:
    POST /api/v1/auth/register  - Register a new user
    POST /api/v1/auth/login     - Login and receive JWT tokens
    POST /api/v1/auth/refresh   - Refresh access token
    POST /api/v1/auth/logout    - Logout (stateless; client discards tokens)
    GET  /api/v1/auth/me        - Get current user profile
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenRefreshRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_by_email,
    get_user_by_id,
    hash_password,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password.get_secret_value()),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.flush()
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: TokenRefreshRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
    )
    try:
        token_data = decode_token(payload.refresh_token)
        if token_data.token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(db, uuid.UUID(token_data.sub))
    if not user or not user.is_active:
        raise credentials_exception

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/logout", status_code=204)
async def logout(current_user: User = Depends(get_current_active_user)) -> Response:
    # Stateless logout — client is responsible for discarding tokens.
    # A Redis token blacklist can be added in a future iteration.
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user
