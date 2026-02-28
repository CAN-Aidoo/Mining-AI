"""
Mining AI Backend - Pytest Configuration and Fixtures.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.main import app

settings = get_settings()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client():
    """Provide an async test client for the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def db_engine():
    """Session-scoped async engine for direct DB access in tests."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def clean_db(db_engine):
    """Truncate all user-data tables before each test to ensure isolation."""
    async with db_engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE TABLE projects, users RESTART IDENTITY CASCADE")
        )
    yield
