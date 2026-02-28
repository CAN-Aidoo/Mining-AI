"""
Mining AI Backend - Auth Endpoint Tests.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_success(async_client: AsyncClient, clean_db) -> None:
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "StrongPass123!", "full_name": "Alice Smith"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice Smith"
    assert "id" in data
    assert "hashed_password" not in data
    assert "password" not in data


@pytest.mark.anyio
async def test_register_duplicate_email(async_client: AsyncClient, clean_db) -> None:
    payload = {"email": "bob@example.com", "password": "Pass123!", "full_name": "Bob"}
    await async_client.post("/api/v1/auth/register", json=payload)
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.anyio
async def test_register_invalid_email(async_client: AsyncClient, clean_db) -> None:
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "Pass123!", "full_name": "Bad"},
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_login_success(async_client: AsyncClient, clean_db) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "carol@example.com", "password": "Pass123!", "full_name": "Carol"},
    )
    resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "carol@example.com", "password": "Pass123!"},
    )
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_wrong_password(async_client: AsyncClient, clean_db) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "dave@example.com", "password": "Correct1!", "full_name": "Dave"},
    )
    resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "dave@example.com", "password": "Wrong1!"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_login_nonexistent_user(async_client: AsyncClient, clean_db) -> None:
    resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "Pass123!"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_me_authenticated(async_client: AsyncClient, clean_db) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "eve@example.com", "password": "Pass123!", "full_name": "Eve"},
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "eve@example.com", "password": "Pass123!"},
    )
    token = login.json()["access_token"]
    resp = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "eve@example.com"


@pytest.mark.anyio
async def test_me_unauthenticated(async_client: AsyncClient) -> None:
    resp = await async_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_me_invalid_token(async_client: AsyncClient) -> None:
    resp = await async_client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer this.is.garbage"}
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_refresh_success(async_client: AsyncClient, clean_db) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "frank@example.com", "password": "Pass123!", "full_name": "Frank"},
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "frank@example.com", "password": "Pass123!"},
    )
    refresh_token = login.json()["refresh_token"]
    resp = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.anyio
async def test_refresh_with_access_token_rejected(async_client: AsyncClient, clean_db) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "grace@example.com", "password": "Pass123!", "full_name": "Grace"},
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "grace@example.com", "password": "Pass123!"},
    )
    access_token = login.json()["access_token"]
    resp = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_logout(async_client: AsyncClient, clean_db) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "henry@example.com", "password": "Pass123!", "full_name": "Henry"},
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "henry@example.com", "password": "Pass123!"},
    )
    token = login.json()["access_token"]
    resp = await async_client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 204
