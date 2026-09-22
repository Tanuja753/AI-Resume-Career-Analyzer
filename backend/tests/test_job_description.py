import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

TEST_DATA_DIR = Path(__file__).parent / "test_data"


def create_test_user_and_login():
    email = (
        f"job_description_test_"
        f"{uuid.uuid4().hex[:8]}@example.com"
    )
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Job Description Test User",
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def create_valid_job_description():
    return {
        "target_job_title": "Backend Developer",
        "description": (
            "We are looking for a Backend Developer "
            "with experience in Python, FastAPI, PostgreSQL, "
            "REST APIs, Git, and Docker. The candidate should "
            "have strong problem-solving skills and experience "
            "building scalable backend applications. "
            "Knowledge of SQL and database design is required."
        ),
    }


def process_job_description(headers):
    return client.post(
        "/job-descriptions/process",
        headers=headers,
        json=create_valid_job_description(),
    )


def upload_test_resume(headers):
    file_path = TEST_DATA_DIR / "test_resume.pdf"

    with file_path.open("rb") as file:
        return client.post(
            "/resumes/upload",
            headers=headers,
            files={
                "file": (
                    "test_resume.pdf",
                    file,
                    "application/pdf",
                )
            },
        )


def test_process_valid_job_description():
    headers = create_test_user_and_login()

    response = process_job_description(headers)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["target_job_title"] == "Backend Developer"
    assert data["raw_description"]
    assert data["cleaned_description"]
    assert data["structured_data"] is not None
    assert data["status"] is not None
    assert "created_at" in data


def test_process_job_description_with_resume_id():
    headers = create_test_user_and_login()

    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    job_data = create_valid_job_description()
    job_data["resume_id"] = resume_id

    response = client.post(
        "/job-descriptions/process",
        headers=headers,
        json=job_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["target_job_title"] == "Backend Developer"
    assert data["id"] > 0


def test_process_job_description_requires_authentication():
    response = client.post(
        "/job-descriptions/process",
        json=create_valid_job_description(),
    )

    assert response.status_code == 401


def test_process_job_description_rejects_short_description():
    headers = create_test_user_and_login()

    response = client.post(
        "/job-descriptions/process",
        headers=headers,
        json={
            "target_job_title": "Backend Developer",
            "description": "Too short",
        },
    )

    assert response.status_code == 422


def test_get_job_description():
    headers = create_test_user_and_login()

    process_response = process_job_description(headers)

    assert process_response.status_code == 201

    job_description_id = process_response.json()["id"]

    response = client.get(
        f"/job-descriptions/{job_description_id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job_description_id
    assert data["target_job_title"] == "Backend Developer"
    assert data["raw_description"]


def test_get_nonexistent_job_description():
    headers = create_test_user_and_login()

    response = client.get(
        "/job-descriptions/999999999",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Job description not found."
    )


def test_extract_job_description_skills():
    headers = create_test_user_and_login()

    process_response = process_job_description(headers)

    assert process_response.status_code == 201

    job_description_id = process_response.json()["id"]

    response = client.post(
        f"/job-descriptions/"
        f"{job_description_id}/skills",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source_id"] == job_description_id
    assert data["source_type"] == "job_description"
    assert "skills" in data
    assert isinstance(data["skills"], list)