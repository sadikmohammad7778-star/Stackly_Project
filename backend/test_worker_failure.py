from app.services.system_health_service import (
    mark_worker_started,
    mark_worker_error,
    mark_worker_heartbeat,
    get_worker_health,
)


def test_worker_error_and_recovery():
    mark_worker_started()

    health = get_worker_health()
    assert health["status"] == "running"

    mark_worker_error("Test worker failure")

    health = get_worker_health()
    assert health["status"] == "degraded"
    assert health["last_error"] == "Test worker failure"

    mark_worker_heartbeat()

    health = get_worker_health()
    assert health["status"] == "running"