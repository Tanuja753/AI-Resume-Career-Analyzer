import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

TEST_DATA_DIR = Path(__file__).parent / "test_data"


def create_test_user_and_login():
    email = (
        f"interview_test_"
        f"{uuid.uuid4().hex[:8]}@example.com"
    )
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Interview Test User",
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


def prepare_interview_data(headers):
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
    # Structure resume
    # ---------------------------------------------------------

    structure_response = client.post(
        f"/resumes/{resume_id}/structure",
        headers=headers,
    )

    assert structure_response.status_code == 200

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
    # Extract JD skills
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


def generate_questions_for_test(headers):
    resume_id, job_description_id = (
        prepare_interview_data(headers)
    )

    response = client.post(
        f"/interview-questions/resume/{resume_id}/"
        f"job-description/{job_description_id}",
        headers=headers,
    )

    return (
        response,
        resume_id,
        job_description_id,
    )


def test_generate_interview_questions_successfully():
    headers = create_test_user_and_login()

    response, resume_id, job_description_id = (
        generate_questions_for_test(headers)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["resume_id"] == resume_id
    assert (
        data["job_description_id"]
        == job_description_id
    )

    assert "questions" in data
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) == 12

    for question in data["questions"]:
        assert "id" in question
        assert "resume_id" in question
        assert "job_description_id" in question
        assert "category" in question
        assert "question" in question
        assert "difficulty" in question
        assert "source" in question


def test_interview_question_category_distribution():
    headers = create_test_user_and_login()

    response, _, _ = generate_questions_for_test(
        headers
    )

    assert response.status_code == 200

    questions = response.json()["questions"]

    category_counts = {}

    for question in questions:
        category = question["category"]

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    assert category_counts["technical"] == 4
    assert category_counts["resume_specific"] == 3
    assert category_counts["behavioral"] == 2
    assert category_counts["scenario"] == 3


def test_get_saved_interview_questions():
    headers = create_test_user_and_login()

    post_response, resume_id, job_description_id = (
        generate_questions_for_test(headers)
    )

    assert post_response.status_code == 200

    response = client.get(
        f"/interview-questions/resume/{resume_id}/"
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

    assert "questions" in data
    assert len(data["questions"]) == 12


def test_get_interview_question_count():
    headers = create_test_user_and_login()

    post_response, resume_id, job_description_id = (
        generate_questions_for_test(headers)
    )

    assert post_response.status_code == 200

    response = client.get(
        f"/interview-questions/resume/{resume_id}/"
        f"job-description/{job_description_id}/count",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["resume_id"] == resume_id
    assert (
        data["job_description_id"]
        == job_description_id
    )

    assert data["question_count"] == 12


def test_generate_interview_questions_requires_authentication():
    response = client.post(
        "/interview-questions/resume/1/"
        "job-description/1",
    )

    assert response.status_code == 401


def test_generate_interview_questions_rejects_missing_resume():
    headers = create_test_user_and_login()

    response = client.post(
        "/interview-questions/resume/999999999/"
        "job-description/1",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Resume not found"
    )


def test_generate_interview_questions_rejects_missing_job_description():
    headers = create_test_user_and_login()

    resume_response = upload_test_resume(headers)

    assert resume_response.status_code == 201

    resume_id = resume_response.json()["id"]

    response = client.post(
        f"/interview-questions/resume/{resume_id}/"
        "job-description/999999999",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Job description not found"
    )