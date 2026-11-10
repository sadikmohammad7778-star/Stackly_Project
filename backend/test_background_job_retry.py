from datetime import timedelta

from app.config.database import SessionLocal
from app.services.background_job_service import (
    create_job,
    start_job,
    fail_job,
    complete_job,
    get_job,
    utc_now,
)


db = SessionLocal()

try:
    job = create_job(
        db=db,
        job_type="integration_sync:999999",
        company_id=3,
        triggered_by=4,
        max_retries=3,
    )

    print("Created Job:", job.id)

    job = start_job(db, job.id)
    print("Started:", job.status)

    for attempt in range(1, 4):
        job = fail_job(
            db,
            job.id,
            f"Controlled retry test failure {attempt}",
        )

        print(
            f"Attempt {attempt}:",
            job.status,
            job.retry_count,
            job.next_retry_at,
        )

        if job.next_retry_at:
            job.next_retry_at = utc_now() - timedelta(seconds=1)
            db.commit()

            job = start_job(db, job.id)
            print("Restarted:", job.status)

    job = fail_job(
        db,
        job.id,
        "Final controlled retry test failure",
    )

    print("Final status:", job.status)
    print("Total retries:", job.retry_count)

finally:
    db.close()