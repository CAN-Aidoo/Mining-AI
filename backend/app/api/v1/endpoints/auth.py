"""
Mining AI Platform - Auth Endpoints (Week 1 Stub).

Routes:
    POST /api/v1/auth/register  - Register a new user
    POST /api/v1/auth/login     - Login and receive JWT tokens
    POST /api/v1/auth/refresh   - Refresh access token
    POST /api/v1/auth/logout    - Invalidate refresh token
    GET  /api/v1/auth/me        - Get current user profile
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/register", summary="Register new user")
async def register() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )


@router.post("/login", summary="Login")
async def login() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )


@router.post("/refresh", summary="Refresh token")
async def refresh_token() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )


@router.post("/logout", summary="Logout")
async def logout() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )


@router.get("/me", summary="Current user")
async def get_current_user() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet - coming in Week 2"},
    )
