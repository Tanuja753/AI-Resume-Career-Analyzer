from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "AI Resume & Career Analyzer API is running"
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_db_session_endpoint():
    response = client.get("/db-session-test")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Database session dependency is working"
    }


def test_database_endpoint():
    response = client.get("/db-test")

    assert response.status_code == 200
    assert response.json() == {
        "message": "PostgreSQL connection successful",
        "result": 1,
    }