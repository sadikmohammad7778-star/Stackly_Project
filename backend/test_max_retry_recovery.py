from datetime import timedelta

from app.config.database import SessionLocal
from app.services.background_job_service import (
    create_job,
    start_job,
    recover_stuck_jobs,
    get_job,
    utc_now,
)

db = SessionLocal()

try:
    job = create_job(
        db=db,
        job_type="integration_sync:999998",
        company_id=3,
        triggered_by=4,
        max_retries=3,
    )

    job = start_job(db, job.id)

    job.retry_count = 3
    job.started_at = utc_now() - timedelta(minutes=20)

    db.commit()

    print("Test Job ID:", job.id)
    print("Before Recovery:", job.status)
    print("Retry Count:", job.retry_count)

    recovered = recover_stuck_jobs(db, timeout_minutes=15)

    print("Recovered Jobs:", recovered)

    job = get_job(db, job.id)

    print("After Recovery:", job.status)
    print("Retry Count:", job.retry_count)
    print("Next Retry:", job.next_retry_at)
    print("Error:", job.error_message)

finally:
    db.close()