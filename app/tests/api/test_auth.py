import pytest
from httpx import AsyncClient
from app.exception.auth_error import AuthenticationError


@pytest.mark.anyio("asyncio")
async def test_register_success(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/register",
        json={
            "phone": "06666666666",
            "full_name": "Test User",
            "password": "strongpassword",
            "avatar_url": "http://example.com/avatar.png",
        },
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert "id" in data["data"]


@pytest.mark.anyio("asyncio")
async def test_register_duplicate_phone(async_client: AsyncClient):
    payload = {
        "phone": "0999999999",
        "full_name": "First User",
        "password": "password1",
        "avatar_url": "http://example.com/avatar1.png",
    }
    # First time should succeed
    await async_client.post("/auth/register", json=payload)

    # Second time should fail
    response = await async_client.post("/auth/register", json=payload)
    assert (
        response.json()["detail"]
        == AuthenticationError.PHONE_ALREADY_EXIST.get_message()
    )


@pytest.mark.anyio("asyncio")
async def test_register_missing_fields(async_client: AsyncClient):
    response = await async_client.post("/auth/register", json={"phone": "022222222"})
    assert response.status_code == 422  # field required


@pytest.mark.anyio("asyncio")
async def test_login_success(async_client: AsyncClient):
    # Register first
    payload = {
        "phone": "0111111111",
        "full_name": "Login Test",
        "password": "secret123",
        "avatar_url": "http://example.com/avatar.png",
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 200, response.json()

    # Then login
    response = await async_client.post(
        "/auth/login", json={"phone": "0111111111", "password": "secret123"}
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert "access_token" in data["data"]


@pytest.mark.anyio("asyncio")
async def test_login_wrong_password(async_client: AsyncClient):
    # Register first
    await async_client.post(
        "/auth/register",
        json={
            "phone": "055555555",
            "full_name": "Wrong Password",
            "password": "correctpass",
            "avatar_url": "",
        },
    )

    # Try login with wrong password
    response = await async_client.post(
        "/auth/login", json={"phone": "055555555", "password": "wrongpass"}
    )
    assert (
        response.json()["detail"]
        == AuthenticationError.INCORRECT_PASSWORD.get_message()
    )
    assert "incorrect" in response.text.lower()


@pytest.mark.anyio("asyncio")
async def test_login_nonexistent_user(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/login", json={"phone": "0000000000", "password": "whatever"}
    )
    assert response.json()["detail"] == AuthenticationError.USER_NOT_FOUND.get_message()
