import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TEST_DATA_DIR = Path(__file__).parent / "test_data"


def create_test_user_and_login():
    email = f"preparation_test_" f"{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Preparation Test User",
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

    return {"Authorization": f"Bearer {token}"}


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


def prepare_preparation_data(headers):
    # --------------------------------------------------
    # 1. Upload resume
    # --------------------------------------------------
    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    # --------------------------------------------------
    # 2. Extract resume text
    # --------------------------------------------------
    extract_response = client.post(
        f"/resumes/{resume_id}/extract",
        headers=headers,
    )

    assert extract_response.status_code == 200

    # --------------------------------------------------
    # 3. Structure resume
    # --------------------------------------------------
    structure_response = client.post(
        f"/resumes/{resume_id}/structure",
        headers=headers,
    )

    assert structure_response.status_code == 200

    # --------------------------------------------------
    # 4. Extract resume skills
    # --------------------------------------------------
    resume_skills_response = client.post(
        f"/resumes/{resume_id}/skills",
        headers=headers,
    )

    assert resume_skills_response.status_code == 200

    # --------------------------------------------------
    # 5. Create job description
    # --------------------------------------------------
    job_response = create_job_description(
        headers,
        resume_id,
    )

    assert job_response.status_code == 201

    job_description_id = job_response.json()["id"]

    # --------------------------------------------------
    # 6. Extract job description skills
    # --------------------------------------------------
    job_skills_response = client.post(
        f"/job-descriptions/" f"{job_description_id}/skills",
        headers=headers,
    )

    assert job_skills_response.status_code == 200

    # --------------------------------------------------
    # 7. Generate skill-gap analysis
    # --------------------------------------------------
    skill_gap_response = client.post(
        f"/skill-gaps/resume/{resume_id}/" f"job-description/{job_description_id}",
        headers=headers,
    )

    assert skill_gap_response.status_code == 200

    # --------------------------------------------------
    # 8. Generate job compatibility
    # --------------------------------------------------
    compatibility_response = client.post(
        f"/job-compatibility/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert compatibility_response.status_code == 200

    # --------------------------------------------------
    # 9. Generate interview questions
    # --------------------------------------------------
    interview_response = client.post(
        f"/interview-questions/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    assert interview_response.status_code == 200

    interview_data = interview_response.json()

    assert len(interview_data["questions"]) == 12

    return resume_id, job_description_id


def generate_preparation_plan_for_test(headers):
    resume_id, job_description_id = prepare_preparation_data(headers)

    response = client.post(
        f"/preparation-plans/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    return (
        response,
        resume_id,
        job_description_id,
    )


def test_generate_preparation_plan_successfully():
    headers = create_test_user_and_login()

    response, resume_id, job_description_id = generate_preparation_plan_for_test(
        headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["resume_id"] == resume_id
    assert data["job_description_id"] == job_description_id

    assert "id" in data
    assert "title" in data
    assert "summary" in data
    assert "estimated_days" in data
    assert "items" in data

    assert data["title"]
    assert data["summary"]
    assert isinstance(data["estimated_days"], int)
    assert data["estimated_days"] > 0

    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
