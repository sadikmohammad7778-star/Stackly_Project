from datetime import datetime, timezone
from threading import Lock

_worker_lock = Lock()

_worker_health = {
    "name": "scheduled_report_worker",
    "status": "not_started",
    "started_at": None,
    "last_heartbeat": None,
    "last_error": None,
    "completed_cycles": 0,
}


def mark_worker_started():
    with _worker_lock:
        _worker_health["status"] = "running"
        _worker_health["started_at"] = datetime.now(timezone.utc).isoformat()
        _worker_health["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        _worker_health["last_error"] = None


def mark_worker_heartbeat():
    with _worker_lock:
        _worker_health["status"] = "running"
        _worker_health["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        _worker_health["completed_cycles"] += 1


def mark_worker_error(error_message):
    with _worker_lock:
        _worker_health["status"] = "degraded"
        _worker_health["last_error"] = str(error_message)
        _worker_health["last_heartbeat"] = datetime.now(timezone.utc).isoformat()


def mark_worker_stopped():
    with _worker_lock:
        _worker_health["status"] = "stopped"
        _worker_health["last_heartbeat"] = datetime.now(timezone.utc).isoformat()


def mark_worker_failed(error_message):
    with _worker_lock:
        _worker_health["status"] = "failed"
        _worker_health["last_error"] = str(error_message)
        _worker_health["last_heartbeat"] = datetime.now(timezone.utc).isoformat()


def get_worker_health():
    with _worker_lock:
        health = dict(_worker_health)

    last_heartbeat = health.get("last_heartbeat")

    if health["status"] == "running" and last_heartbeat:
        heartbeat_time = datetime.fromisoformat(last_heartbeat)
        elapsed = (
            datetime.now(timezone.utc) - heartbeat_time
        ).total_seconds()

        if elapsed > 90:
            health["status"] = "degraded"
            health["last_error"] = "Worker heartbeat is stale"

    return health