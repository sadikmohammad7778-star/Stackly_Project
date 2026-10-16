from unittest.mock import patch
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.health_routes import router


app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_health_details_healthy():
    with patch(
        "app.routes.health_routes.get_worker_health",
        return_value={
            "name": "scheduled_report_worker",
            "status": "running",
            "started_at": "2026-10-15T06:00:00+00:00",
            "last_heartbeat": "2026-10-15T06:00:10+00:00",
            "last_error": None,
            "completed_cycles": 3,
        },
    ):
        response = client.get("/health/details")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_details_degraded_worker():
    with patch(
        "app.routes.health_routes.get_worker_health",
        return_value={
            "name": "scheduled_report_worker",
            "status": "degraded",
            "started_at": "2026-10-15T06:00:00+00:00",
            "last_heartbeat": "2026-10-15T06:00:10+00:00",
            "last_error": "Worker heartbeat is stale",
            "completed_cycles": 3,
        },
    ):
        response = client.get("/health/details")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"


def test_health_details_failed_worker():
    with patch(
        "app.routes.health_routes.get_worker_health",
        return_value={
            "name": "scheduled_report_worker",
            "status": "failed",
            "started_at": "2026-10-15T06:00:00+00:00",
            "last_heartbeat": "2026-10-15T06:00:10+00:00",
            "last_error": "Scheduled report worker terminated unexpectedly",
            "completed_cycles": 3,
        },
    ):
        response = client.get("/health/details")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"


def test_health_details_database_unavailable():
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("Database unavailable")

    app.dependency_overrides[
        __import__(
            "app.routes.health_routes",
            fromlist=["get_db"],
        ).get_db
    ] = lambda: mock_db

    try:
        with patch(
            "app.routes.health_routes.get_worker_health",
            return_value={
                "name": "scheduled_report_worker",
                "status": "running",
                "started_at": "2026-10-15T06:00:00+00:00",
                "last_heartbeat": "2026-10-15T06:00:10+00:00",
                "last_error": None,
                "completed_cycles": 3,
            },
        ):
            response = client.get("/health/details")

        assert response.status_code == 503
        assert response.json()["status"] == "unavailable"
        assert response.json()["components"]["database"]["status"] == "unavailable"
    finally:
        app.dependency_overrides.clear()