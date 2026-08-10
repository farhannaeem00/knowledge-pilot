"""
Real integration tests for the auth flow: register, login, /me, refresh
rotation, and logout revocation. Mirrors exactly what we manually
verified in Step 3, now automated.
"""
import pytest

pytestmark = pytest.mark.asyncio


async def test_register_creates_user_without_password_hash(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "pytest@example.com", "password": "testpassword123", "full_name": "Pytest User"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "pytest@example.com"
    assert "password_hash" not in body


async def test_register_duplicate_email_rejected(client):
    payload = {"email": "dup@example.com", "password": "testpassword123", "full_name": "Dup"}
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


async def test_login_and_me(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "loginme@example.com", "password": "testpassword123", "full_name": "Login Me"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "loginme@example.com", "password": "testpassword123"}
    )
    assert login.status_code == 200
    tokens = login.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "loginme@example.com"


async def test_login_wrong_password_rejected(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@example.com", "password": "correctpassword", "full_name": "X"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "wrongpw@example.com", "password": "wrongpassword"}
    )
    assert login.status_code == 401


async def test_refresh_token_rotates_and_old_token_is_rejected(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "rotate@example.com", "password": "testpassword123", "full_name": "Rotate"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "rotate@example.com", "password": "testpassword123"}
    )
    old_refresh = login.json()["refresh_token"]

    refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refreshed.status_code == 200
    new_refresh = refreshed.json()["refresh_token"]
    assert new_refresh != old_refresh

    reuse_attempt = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse_attempt.status_code == 401


async def test_logout_revokes_refresh_token(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "logout@example.com", "password": "testpassword123", "full_name": "Logout"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "logout@example.com", "password": "testpassword123"}
    )
    refresh_token = login.json()["refresh_token"]

    logout = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout.status_code == 204

    reuse_attempt = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse_attempt.status_code == 401


async def test_me_without_token_rejected(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401