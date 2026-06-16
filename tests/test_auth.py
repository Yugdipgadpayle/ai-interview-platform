"""Authentication endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_and_me(client: AsyncClient) -> None:
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "dev@example.com", "full_name": "Dev User", "password": "strongpass123"},
    )
    assert register.status_code == 201
    assert register.json()["email"] == "dev@example.com"

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "dev@example.com", "password": "strongpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["full_name"] == "Dev User"
