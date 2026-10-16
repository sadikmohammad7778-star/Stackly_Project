import logging
from datetime import datetime, timezone
from time import perf_counter

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.services.system_health_service import get_worker_health
from app.middleware.performance_monitoring import (
    get_api_metrics,
    get_api_performance_summary,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["System Health"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def health():
    return {
        "status": "healthy",
        "application": "RetailPulse Analytics",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/details")
def detailed_health(db: Session = Depends(get_db)):
    components = {
        "api": {
            "status": "healthy"
        }
    }

    start_time = perf_counter()

    try:
        db.execute(text("SELECT 1"))

        response_time_ms = round(
            (perf_counter() - start_time) * 1000,
            2,
        )

        components["database"] = {
            "status": "healthy",
            "response_time_ms": response_time_ms,
        }

    except Exception:
        logger.exception("System health database check failed")

        components["database"] = {
            "status": "unavailable"
        }

    worker_health = get_worker_health()
    components["background_processor"] = worker_health

    database_healthy = (
        components["database"]["status"] == "healthy"
    )

    worker_status = str(
        worker_health.get("status", "unknown")
    ).lower()

    unhealthy_worker_statuses = {
        "failed",
        "stopped",
        "unavailable",
        "unknown",
    }

    degraded_worker_statuses = {
        "degraded",
        "not_started",
    }

    if not database_healthy:
        overall_status = "unavailable"
        http_status = 503
    elif worker_status in unhealthy_worker_statuses:
        overall_status = "unavailable"
        http_status = 503
    elif worker_status in degraded_worker_statuses:
        overall_status = "degraded"
        http_status = 200
    else:
        overall_status = "healthy"
        http_status = 200

    response = {
        "status": overall_status,
        "application": "RetailPulse Analytics",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": components,
    }

    return JSONResponse(
        status_code=http_status,
        content=response,
    )


@router.get("/performance")
def api_performance():
    return get_api_performance_summary()


@router.get("/performance/metrics")
def api_performance_metrics():
    metrics = get_api_metrics()

    return {
        "total_records": len(metrics),
        "metrics": metrics,
    }