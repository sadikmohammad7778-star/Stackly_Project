from datetime import datetime, timezone
from time import perf_counter
from collections import deque
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


MAX_METRICS = 10000

EXCLUDED_PATHS = {
    "/",
    "/health/",
    "/health/details",
    "/health/performance",
    "/health/performance/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
}

_api_metrics = deque(maxlen=MAX_METRICS)
_metrics_lock = Lock()


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat()
        response_status = 500

        try:
            response = await call_next(request)
            response_status = response.status_code
            return response

        finally:
            response_time_ms = round(
                (perf_counter() - start_time) * 1000,
                2,
            )

            if request.url.path not in EXCLUDED_PATHS:
                metric = {
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": response_status,
                    "response_time_ms": response_time_ms,
                    "timestamp": timestamp,
                    "success": 200 <= response_status < 400,
                }

                with _metrics_lock:
                    _api_metrics.append(metric)


def get_api_metrics():
    with _metrics_lock:
        return list(_api_metrics)


def get_api_performance_summary():
    metrics = get_api_metrics()

    total_requests = len(metrics)

    successful_requests = sum(
        1 for metric in metrics if metric["success"]
    )

    failed_requests = total_requests - successful_requests

    average_response_time = (
        round(
            sum(
                metric["response_time_ms"]
                for metric in metrics
            ) / total_requests,
            2,
        )
        if total_requests
        else 0
    )

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_response_time_ms": average_response_time,
    }