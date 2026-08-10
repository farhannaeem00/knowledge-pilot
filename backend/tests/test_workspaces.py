"""
Real integration tests for workspace CRUD and, critically, ownership
isolation - this is the automated version of the "no cross-user data
leakage" NFR, not just a documented intention.
"""
import pytest

pytestmark = pytest.mark.asyncio


async def _register_and_login(client, email: str) -> dict:
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "testpassword123", "full_name": "Test"}
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "testpassword123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_and_list_workspace(client):
    headers = await _register_and_login(client, "ws1@example.com")

    created = await client.post("/api/v1/workspaces", json={"name": "My Workspace"}, headers=headers)
    assert created.status_code == 201
    assert created.json()["name"] == "My Workspace"

    listed = await client.get("/api/v1/workspaces", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


async def test_workspace_isolation_between_users(client):
    """
    The core data-isolation test: user B must never be able to see or
    access user A's workspace, by ID or by listing.
    """
    headers_a = await _register_and_login(client, "isoA@example.com")
    headers_b = await _register_and_login(client, "isoB@example.com")

    created = await client.post("/api/v1/workspaces", json={"name": "A's Private Workspace"}, headers=headers_a)
    workspace_id = created.json()["id"]

    # User B tries to fetch user A's workspace directly by ID.
    stolen = await client.get(f"/api/v1/workspaces/{workspace_id}", headers=headers_b)
    assert stolen.status_code == 404  # not 403 - existence itself isn't confirmed

    # User B's own list must not include it.
    b_list = await client.get("/api/v1/workspaces", headers=headers_b)
    assert all(w["id"] != workspace_id for w in b_list.json())


async def test_delete_workspace_is_soft_delete(client):
    headers = await _register_and_login(client, "softdel@example.com")
    created = await client.post("/api/v1/workspaces", json={"name": "Temp"}, headers=headers)
    workspace_id = created.json()["id"]

    deleted = await client.delete(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert deleted.status_code == 204

    # Soft-deleted workspace should no longer appear in the default list...
    listed = await client.get("/api/v1/workspaces", headers=headers)
    assert all(w["id"] != workspace_id for w in listed.json())

    # ...and direct access should now 404 (status == "trashed" excluded).
    fetched = await client.get(f"/api/v1/workspaces/{workspace_id}", headers=headers)
    assert fetched.status_code == 404