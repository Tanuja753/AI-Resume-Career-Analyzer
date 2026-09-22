import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_user():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": password,
        },
    )

    return email, password, response


def test_user_registration():
    email, password, response = create_test_user()

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Test User"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_duplicate_registration_is_rejected():
    email, password, first_response = create_test_user()

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Another User",
            "password": password,
        },
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "A user with this email already exists"
    )


def test_login_with_valid_credentials():
    email, password, registration_response = create_test_user()

    assert registration_response.status_code == 201

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_with_invalid_password():
    email, password, registration_response = create_test_user()

    assert registration_response.status_code == 201

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_protected_me_endpoint_requires_authentication():
    response = client.get("/auth/me")

    assert response.status_code == 401