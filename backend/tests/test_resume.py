import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

TEST_DATA_DIR = Path(__file__).parent / "test_data"


def create_test_user_and_login():
    email = f"resume_test_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Resume Test User",
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


def upload_resume(headers, filename):
    file_path = TEST_DATA_DIR / filename

    with file_path.open("rb") as file:
        return client.post(
            "/resumes/upload",
            headers=headers,
            files={
                "file": (
                    filename,
                    file,
                    (
                        "application/pdf"
                        if filename.endswith(".pdf")
                        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    ),
                )
            },
        )


def test_upload_pdf_resume():
    headers = create_test_user_and_login()

    response = upload_resume(
        headers,
        "test_resume.pdf",
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["original_filename"] == "test_resume.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["file_size"] > 0
    assert data["status"] is not None


def test_upload_docx_resume():
    headers = create_test_user_and_login()

    response = upload_resume(
        headers,
        "test_resume.docx",
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["original_filename"] == "test_resume.docx"
    assert (
        data["content_type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert data["file_size"] > 0


def test_upload_requires_authentication():
    file_path = TEST_DATA_DIR / "test_resume.pdf"

    with file_path.open("rb") as file:
        response = client.post(
            "/resumes/upload",
            files={
                "file": (
                    "test_resume.pdf",
                    file,
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 401


def test_upload_rejects_unsupported_file_type():
    headers = create_test_user_and_login()

    response = client.post(
        "/resumes/upload",
        headers=headers,
        files={
            "file": (
                "test_resume.txt",
                b"This is not a supported resume file.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_extract_resume():
    headers = create_test_user_and_login()

    upload_response = upload_resume(
        headers,
        "test_resume.pdf",
    )

    assert upload_response.status_code == 201

    resume_id = upload_response.json()["id"]

    response = client.post(
        f"/resumes/{resume_id}/extract",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == resume_id
    assert data["original_filename"] == "test_resume.pdf"
    assert data["extracted_text"]
    assert "Test User" in data["extracted_text"]


def test_structure_resume():
    headers = create_test_user_and_login()

    upload_response = upload_resume(
        headers,
        "test_resume.pdf",
    )

    assert upload_response.status_code == 201

    resume_id = upload_response.json()["id"]

    extract_response = client.post(
        f"/resumes/{resume_id}/extract",
        headers=headers,
    )

    assert extract_response.status_code == 200

    response = client.post(
        f"/resumes/{resume_id}/structure",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == resume_id


def test_extract_resume_skills():
    headers = create_test_user_and_login()

    upload_response = upload_resume(
        headers,
        "test_resume.pdf",
    )

    assert upload_response.status_code == 201

    resume_id = upload_response.json()["id"]

    extract_response = client.post(
        f"/resumes/{resume_id}/extract",
        headers=headers,
    )

    assert extract_response.status_code == 200

    response = client.post(
        f"/resumes/{resume_id}/skills",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source_id"] == resume_id
    assert data["source_type"] == "resume"
    assert "skills" in data
    assert isinstance(data["skills"], list)