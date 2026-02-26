"""
Mining AI Backend - Health Endpoint Smoke Tests.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check(async_client: AsyncClient) -> None:
    """Verify /health returns 200 with expected shape."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


@pytest.mark.anyio
async def test_health_check_returns_json(async_client: AsyncClient) -> None:
    """Verify /health response Content-Type is application/json."""
    response = await async_client.get("/health")
    assert "application/json" in response.headers["content-type"]


@pytest.mark.anyio
async def test_stub_routes_return_501(async_client: AsyncClient) -> None:
    """Verify all stub routes are registered (return 501, not 404)."""
    stub_routes = [
        "/api/v1/research/",
        "/api/v1/documents/",
        "/api/v1/prototypes/",
        "/api/v1/projects/",
        "/api/v1/auth/me",
    ]
    for route in stub_routes:
        response = await async_client.get(route)
        assert response.status_code == 501, (
            f"Expected 501 from {route}, got {response.status_code}"
        )
