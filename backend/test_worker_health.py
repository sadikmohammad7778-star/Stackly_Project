from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.services.system_health_service import get_worker_health


def test_stale_worker_heartbeat():
    old_heartbeat = (
        datetime.now(timezone.utc) - timedelta(seconds=120)
    ).isoformat()

    mock_health = {
        "name": "scheduled_report_worker",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "last_heartbeat": old_heartbeat,
        "last_error": None,
        "completed_cycles": 1,
    }

    with patch(
        "app.services.system_health_service._worker_health",
        mock_health.copy(),
    ):
        health = get_worker_health()

    assert health["status"] == "degraded"
    assert health["last_error"] == "Worker heartbeat is stale"