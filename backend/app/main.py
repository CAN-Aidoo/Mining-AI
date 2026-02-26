"""
Mining AI Platform - FastAPI Application Entry Point.

Configures the application instance, middleware, routers, and lifecycle events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown events."""
    logger.info(
        "Starting Mining AI API",
        environment=settings.ENVIRONMENT,
        version="0.1.0",
    )
    # Future: initialize DB pool, ChromaDB client, warm caches here
    yield
    logger.info("Shutting down Mining AI API")
    # Future: close DB pool, flush queues here


def create_application() -> FastAPI:
    """Application factory pattern."""
    application = FastAPI(
        title="Mining AI Platform API",
        description="AI-powered research and prototype generation for final year students",
        version="0.1.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix="/api/v1")

    return application


app = create_application()


@app.get("/health", tags=["health"], summary="Health check")
async def health_check() -> dict:
    """Returns 200 if the API is running."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
    }
