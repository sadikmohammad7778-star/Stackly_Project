import asyncio
from unittest.mock import MagicMock, patch

import pytest

from app.services.report_scheduler_service import scheduled_report_worker
from app.services.system_health_service import get_worker_health


@pytest.mark.asyncio
async def test_scheduler_polling_failure_and_recovery():
    db = MagicMock()
    db.query.side_effect = [
        RuntimeError("Simulated database polling failure"),
        MagicMock(),
    ]

    async def fake_sleep(seconds):
        if db.query.call_count >= 2:
            raise asyncio.CancelledError()

    with patch(
        "app.services.report_scheduler_service.SessionLocal",
        return_value=db,
    ), patch(
        "app.services.report_scheduler_service.asyncio.sleep",
        side_effect=fake_sleep,
    ):
        with pytest.raises(asyncio.CancelledError):
            await scheduled_report_worker()

    health = get_worker_health()

    assert db.query.call_count == 2
    assert health["completed_cycles"] >= 1
    assert health["status"] == "stopped"