import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

TEST_DATA_DIR = Path(__file__).parent / "test_data"


def create_test_user_and_login():
    email = (
        f"skill_gap_test_"
        f"{uuid.uuid4().hex[:8]}@example.com"
    )
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Skill Gap Test User",
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


def create_job_description(headers, resume_id=None):
    job_data = {
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

    if resume_id is not None:
        job_data["resume_id"] = resume_id

    return client.post(
        "/job-descriptions/process",
        headers=headers,
        json=job_data,
    )


def prepare_complete_analysis_data(headers):
    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    extract_response = client.post(
        f"/resumes/{resume_id}/extract",
        headers=headers,
    )

    assert extract_response.status_code == 200

    resume_skills_response = client.post(
        f"/resumes/{resume_id}/skills",
        headers=headers,
    )

    assert resume_skills_response.status_code == 200

    job_response = create_job_description(
        headers,
        resume_id,
    )

    assert job_response.status_code == 201

    job_description_id = job_response.json()["id"]

    job_skills_response = client.post(
        f"/job-descriptions/"
        f"{job_description_id}/skills",
        headers=headers,
    )

    assert job_skills_response.status_code == 200

    return resume_id, job_description_id


def test_analyze_skill_gaps_successfully():
    headers = create_test_user_and_login()

    resume_id, job_description_id = (
        prepare_complete_analysis_data(headers)
    )

    response = client.post(
        f"/skill-gaps/resume/{resume_id}/"
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

    assert "matched_skills" in data
    assert "partial_skills" in data
    assert "missing_skills" in data
    assert "summary" in data

    assert isinstance(
        data["matched_skills"],
        list,
    )

    assert isinstance(
        data["partial_skills"],
        list,
    )

    assert isinstance(
        data["missing_skills"],
        list,
    )


def test_get_saved_skill_gap_analysis():
    headers = create_test_user_and_login()

    resume_id, job_description_id = (
        prepare_complete_analysis_data(headers)
    )

    post_response = client.post(
        f"/skill-gaps/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert post_response.status_code == 200

    response = client.get(
        f"/skill-gaps/resume/{resume_id}/"
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

    assert "summary" in data

    summary = data["summary"]

    assert "total_required" in summary
    assert "matched" in summary
    assert "partial" in summary
    assert "missing" in summary

    assert (
        summary["total_required"]
        >= 0
    )


def test_analyze_skill_gaps_requires_authentication():
    response = client.post(
        "/skill-gaps/resume/1/job-description/1",
    )

    assert response.status_code == 401


def test_analyze_skill_gaps_rejects_missing_resume():
    headers = create_test_user_and_login()

    response = client.post(
        "/skill-gaps/resume/999999999/"
        "job-description/1",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Resume not found"
    )


def test_analyze_skill_gaps_rejects_missing_job_description():
    headers = create_test_user_and_login()

    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    response = client.post(
        f"/skill-gaps/resume/{resume_id}/"
        "job-description/999999999",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Job description not found"
    )


def test_analyze_skill_gaps_requires_resume_skills():
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

    job_skills_response = client.post(
        f"/job-descriptions/"
        f"{job_description_id}/skills",
        headers=headers,
    )

    assert job_skills_response.status_code == 200

    response = client.post(
        f"/skill-gaps/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Resume skills have not been extracted yet"
    )


def test_analyze_skill_gaps_requires_job_description_skills():
    headers = create_test_user_and_login()

    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    resume_extract_response = client.post(
        f"/resumes/{resume_id}/extract",
        headers=headers,
    )

    assert resume_extract_response.status_code == 200

    resume_skills_response = client.post(
        f"/resumes/{resume_id}/skills",
        headers=headers,
    )

    assert resume_skills_response.status_code == 200

    job_response = create_job_description(
        headers,
        resume_id,
    )

    assert job_response.status_code == 201

    job_description_id = job_response.json()["id"]

    response = client.post(
        f"/skill-gaps/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Job description skills have not "
        "been extracted yet"
    )