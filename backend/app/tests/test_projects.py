"""
Mining AI Backend - Projects Endpoint Tests.
"""

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str) -> str:
    """Helper: register a user and return an access token."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Pass123!", "full_name": "Test User"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "Pass123!"},
    )
    return login.json()["access_token"]


@pytest.mark.anyio
async def test_list_projects_empty(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "list@example.com")
    resp = await async_client.get(
        "/api/v1/projects/", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.anyio
async def test_list_projects_requires_auth(async_client: AsyncClient) -> None:
    resp = await async_client.get("/api/v1/projects/")
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_create_project_success(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "create@example.com")
    resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "My FYP", "field": "computer_science"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My FYP"
    assert data["field"] == "computer_science"
    assert data["status"] == "draft"
    assert "id" in data
    assert "owner_id" in data


@pytest.mark.anyio
async def test_create_project_with_description(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "desc@example.com")
    resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "Described Project", "description": "A great project.", "field": "engineering"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["description"] == "A great project."


@pytest.mark.anyio
async def test_create_project_invalid_field(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "invalid@example.com")
    resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "Bad Project", "field": "underwater_basket_weaving"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_project_missing_title(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "notitle@example.com")
    resp = await async_client.post(
        "/api/v1/projects/",
        json={"field": "business"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_get_project_success(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "get@example.com")
    create_resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "To Fetch", "field": "engineering"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_resp.json()["id"]
    resp = await async_client.get(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == project_id


@pytest.mark.anyio
async def test_get_project_not_found(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "missing@example.com")
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await async_client.get(
        f"/api/v1/projects/{fake_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_get_project_other_user_returns_404(async_client: AsyncClient, clean_db) -> None:
    token_a = await _register_and_login(async_client, "owner@example.com")
    token_b = await _register_and_login(async_client, "other@example.com")
    create_resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "Secret Project", "field": "business"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    project_id = create_resp.json()["id"]
    resp = await async_client.get(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_update_project_partial(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "update@example.com")
    create_resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "Original Title", "field": "engineering"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_resp.json()["id"]
    resp = await async_client.patch(
        f"/api/v1/projects/{project_id}",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "in_progress"
    assert data["title"] == "Original Title"  # unchanged


@pytest.mark.anyio
async def test_update_project_not_owned(async_client: AsyncClient, clean_db) -> None:
    token_a = await _register_and_login(async_client, "uowner@example.com")
    token_b = await _register_and_login(async_client, "uother@example.com")
    create_resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "Not Yours", "field": "business"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    project_id = create_resp.json()["id"]
    resp = await async_client.patch(
        f"/api/v1/projects/{project_id}",
        json={"title": "Hijacked"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_delete_project_success(async_client: AsyncClient, clean_db) -> None:
    token = await _register_and_login(async_client, "delete@example.com")
    create_resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "To Delete", "field": "health_sciences"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_resp.json()["id"]
    resp = await async_client.delete(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 204
    # Confirm it's gone
    get_resp = await async_client.get(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_delete_project_not_owned(async_client: AsyncClient, clean_db) -> None:
    token_a = await _register_and_login(async_client, "downer@example.com")
    token_b = await _register_and_login(async_client, "dother@example.com")
    create_resp = await async_client.post(
        "/api/v1/projects/",
        json={"title": "Protected", "field": "computer_science"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    project_id = create_resp.json()["id"]
    resp = await async_client.delete(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_list_scoped_to_owner(async_client: AsyncClient, clean_db) -> None:
    token_a = await _register_and_login(async_client, "scopeA@example.com")
    token_b = await _register_and_login(async_client, "scopeB@example.com")
    # A creates a project
    await async_client.post(
        "/api/v1/projects/",
        json={"title": "A's Project", "field": "computer_science"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    # B should see zero projects
    resp = await async_client.get(
        "/api/v1/projects/", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.json()["total"] == 0
    # A should see one project
    resp_a = await async_client.get(
        "/api/v1/projects/", headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp_a.json()["total"] == 1
