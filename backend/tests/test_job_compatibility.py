import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

TEST_DATA_DIR = Path(__file__).parent / "test_data"


def create_test_user_and_login():
    email = (
        f"compatibility_test_"
        f"{uuid.uuid4().hex[:8]}@example.com"
    )
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Compatibility Test User",
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


def create_job_description(headers, resume_id):
    return client.post(
        "/job-descriptions/process",
        headers=headers,
        json={
            "target_job_title": "Backend Developer",
            "description": (
                "We are looking for a Backend Developer "
                "with experience in Python, FastAPI, PostgreSQL, "
                "REST APIs, Git, and Docker. The candidate should "
                "have strong problem-solving skills and experience "
                "building scalable backend applications. "
                "Knowledge of SQL and database design is required."
            ),
            "resume_id": resume_id,
        },
    )


def prepare_compatibility_data(headers):
    # ---------------------------------------------------------
    # Upload resume
    # ---------------------------------------------------------

    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    # ---------------------------------------------------------
    # Extract resume text
    # ---------------------------------------------------------

    extract_response = client.post(
        f"/resumes/{resume_id}/extract",
        headers=headers,
    )

    assert extract_response.status_code == 200

    # ---------------------------------------------------------
    # Extract resume skills
    # ---------------------------------------------------------

    resume_skills_response = client.post(
        f"/resumes/{resume_id}/skills",
        headers=headers,
    )

    assert resume_skills_response.status_code == 200

    # ---------------------------------------------------------
    # Process job description
    # ---------------------------------------------------------

    job_response = create_job_description(
        headers,
        resume_id,
    )

    assert job_response.status_code == 201

    job_description_id = job_response.json()["id"]

    # ---------------------------------------------------------
    # Extract job description skills
    # ---------------------------------------------------------

    job_skills_response = client.post(
        f"/job-descriptions/"
        f"{job_description_id}/skills",
        headers=headers,
    )

    assert job_skills_response.status_code == 200

# ---------------------------------------------------------
# Run skill gap analysis
# ---------------------------------------------------------

    skill_gap_response = client.post(
        f"/skill-gaps/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert skill_gap_response.status_code == 200

    return resume_id, job_description_id

def test_analyze_job_compatibility_successfully():
    headers = create_test_user_and_login()

    resume_id, job_description_id = (
        prepare_compatibility_data(headers)
    )

    response = client.post(
        f"/job-compatibility/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )
    

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["resume_id"] == resume_id
    assert (
        data["job_description_id"]
        == job_description_id
    )

    assert "total_required" in data
    assert "matched" in data
    assert "partial" in data
    assert "missing" in data

    assert "explanation" in data
    assert isinstance(
        data["explanation"],
        str,
    )


def test_compatibility_score_fields_are_valid():
    headers = create_test_user_and_login()

    resume_id, job_description_id = (
        prepare_compatibility_data(headers)
    )

    response = client.post(
        f"/job-compatibility/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert 0 <= data["skill_coverage_percentage"] <= 100
    assert 0 <= data["semantic_match_percentage"] <= 100
    assert 0 <= data["compatibility_score"] <= 100

    assert data["total_required"] >= 0
    assert data["matched"] >= 0
    assert data["partial"] >= 0
    assert data["missing"] >= 0


def test_get_saved_job_compatibility():
    headers = create_test_user_and_login()

    resume_id, job_description_id = (
        prepare_compatibility_data(headers)
    )

    post_response = client.post(
        f"/job-compatibility/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert post_response.status_code == 200

    response = client.get(
        f"/job-compatibility/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["resume_id"] == resume_id
    assert (
        data["job_description_id"]
        == job_description_id
    )

    assert "compatibility_score" in data
    assert "explanation" in data


def test_analyze_job_compatibility_requires_authentication():
    response = client.post(
        "/job-compatibility/resume/1/"
        "job-description/1",
    )

    assert response.status_code == 401


def test_analyze_job_compatibility_rejects_missing_resume():
    headers = create_test_user_and_login()

    response = client.post(
        "/job-compatibility/resume/999999999/"
        "job-description/1",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Resume not found"
    )


def test_analyze_job_compatibility_rejects_missing_job_description():
    headers = create_test_user_and_login()

    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    response = client.post(
        f"/job-compatibility/resume/{resume_id}/"
        "job-description/999999999",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Job description not found"
    )


def test_get_missing_job_compatibility():
    headers = create_test_user_and_login()

    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    job_response = create_job_description(
        headers,
        resume_id,
    )

    assert job_response.status_code == 201

    job_description_id = job_response.json()["id"]

    response = client.get(
        f"/job-compatibility/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Compatibility analysis not found"
    )