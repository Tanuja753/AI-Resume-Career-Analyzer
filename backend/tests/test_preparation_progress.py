from tests.test_preparation_plan import (
    client,
    create_test_user_and_login,
    generate_preparation_plan_for_test,
)


def prepare_progress_data():
    headers = create_test_user_and_login()

    response, resume_id, job_description_id = generate_preparation_plan_for_test(
        headers
    )

    assert response.status_code == 200

    plan_data = response.json()

    assert "id" in plan_data
    assert "items" in plan_data
    assert len(plan_data["items"]) > 0

    return (
        headers,
        resume_id,
        job_description_id,
        plan_data,
    )


def test_get_initial_preparation_progress():
    (
        headers,
        resume_id,
        job_description_id,
        plan_data,
    ) = prepare_progress_data()

    response = client.get(
        f"/preparation-plans/resume/{resume_id}/"
        f"job-description/{job_description_id}/progress",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["resume_id"] == resume_id
    assert data["job_description_id"] == job_description_id
    assert data["plan_id"] == plan_data["id"]

    assert "summary" in data
    assert "items" in data

    summary = data["summary"]

    assert summary["total_items"] == len(plan_data["items"])
    assert summary["not_started"] == len(plan_data["items"])
    assert summary["in_progress"] == 0
    assert summary["completed"] == 0
    assert summary["progress_percentage"] == 0.0

    assert len(data["items"]) == len(plan_data["items"])

    for item in data["items"]:
        assert item["status"] == "not_started"
        assert item["notes"] is None
        assert item["completed_at"] is None


def test_update_preparation_progress_to_in_progress():
    (
        headers,
        resume_id,
        job_description_id,
        plan_data,
    ) = prepare_progress_data()

    plan_item_id = plan_data["items"][0]["id"]

    response = client.patch(
        f"/preparation-plans/items/{plan_item_id}/progress",
        headers=headers,
        json={
            "status": "in_progress",
            "notes": "Started studying this topic.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["plan_item_id"] == plan_item_id
    assert data["status"] == "in_progress"
    assert data["notes"] == "Started studying this topic."
    assert data["completed_at"] is None


def test_update_preparation_progress_to_completed():
    (
        headers,
        resume_id,
        job_description_id,
        plan_data,
    ) = prepare_progress_data()

    plan_item_id = plan_data["items"][0]["id"]

    response = client.patch(
        f"/preparation-plans/items/{plan_item_id}/progress",
        headers=headers,
        json={
            "status": "completed",
            "notes": "Completed this topic successfully.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["plan_item_id"] == plan_item_id
    assert data["status"] == "completed"
    assert data["notes"] == "Completed this topic successfully."
    assert data["completed_at"] is not None


def test_progress_summary_after_completion():
    (
        headers,
        resume_id,
        job_description_id,
        plan_data,
    ) = prepare_progress_data()

    plan_item_id = plan_data["items"][0]["id"]
    total_items = len(plan_data["items"])

    response = client.patch(
        f"/preparation-plans/items/{plan_item_id}/progress",
        headers=headers,
        json={
            "status": "completed",
            "notes": "Completed.",
        },
    )

    assert response.status_code == 200

    progress_response = client.get(
        f"/preparation-plans/resume/{resume_id}/"
        f"job-description/{job_description_id}/progress",
        headers=headers,
    )

    assert progress_response.status_code == 200

    data = progress_response.json()
    summary = data["summary"]

    assert summary["total_items"] == total_items
    assert summary["completed"] == 1
    assert summary["not_started"] == total_items - 1
    assert summary["in_progress"] == 0

    expected_percentage = round(
        (1 / total_items) * 100,
        2,
    )

    assert summary["progress_percentage"] == expected_percentage


def test_update_nonexistent_plan_item():
    headers = create_test_user_and_login()

    response = client.patch(
        "/preparation-plans/items/999999/progress",
        headers=headers,
        json={
            "status": "completed",
            "notes": "This should fail.",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Preparation plan item not found."


def test_get_progress_for_nonexistent_resume():
    headers = create_test_user_and_login()

    response = client.get(
        "/preparation-plans/resume/999999/" "job-description/999999/progress",
        headers=headers,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Resume not found."


def test_invalid_progress_status():
    (
        headers,
        resume_id,
        job_description_id,
        plan_data,
    ) = prepare_progress_data()

    plan_item_id = plan_data["items"][0]["id"]

    response = client.patch(
        f"/preparation-plans/items/{plan_item_id}/progress",
        headers=headers,
        json={
            "status": "invalid_status",
            "notes": "Invalid status test.",
        },
    )

    assert response.status_code == 422
