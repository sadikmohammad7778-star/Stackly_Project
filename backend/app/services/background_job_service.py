from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.background_job import BackgroundJob


RETRY_BASE_DELAY_SECONDS = 30
MAX_RETRY_DELAY_SECONDS = 1800
DEFAULT_MAX_RETRIES = 3
JOB_TIMEOUT_MINUTES = 15


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_job(
    db: Session,
    job_type: str,
    company_id: int = None,
    triggered_by: int = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
):
    job = BackgroundJob(
        job_type=job_type,
        company_id=company_id,
        triggered_by=triggered_by,
        status="Pending",
        retry_count=0,
        max_retries=max_retries,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def start_job(db: Session, job_id: int):
    job = (
        db.query(BackgroundJob)
        .filter(BackgroundJob.id == job_id)
        .with_for_update()
        .first()
    )

    if not job:
        return None

    if job.status != "Pending":
        return job

    now = utc_now()

    job.status = "Running"
    job.started_at = now
    job.completed_at = None
    job.error_message = None
    job.next_retry_at = None

    db.commit()
    db.refresh(job)

    return job


def complete_job(db: Session, job_id: int):
    job = (
        db.query(BackgroundJob)
        .filter(BackgroundJob.id == job_id)
        .with_for_update()
        .first()
    )

    if not job:
        return None

    if job.status != "Running":
        return job

    job.completed_at = utc_now()
    job.status = "Completed"
    job.next_retry_at = None
    job.error_message = None

    if job.started_at:
        job.duration_ms = max(
            0,
            int(
                (job.completed_at - job.started_at).total_seconds()
                * 1000
            ),
        )

    db.commit()
    db.refresh(job)

    return job


def fail_job(
    db: Session,
    job_id: int,
    error_message: str,
):
    job = (
        db.query(BackgroundJob)
        .filter(BackgroundJob.id == job_id)
        .with_for_update()
        .first()
    )

    if not job:
        return None

    if job.status not in ("Pending", "Running"):
        return job

    now = utc_now()

    job.error_message = error_message[:2000]
    job.completed_at = now

    if job.started_at:
        job.duration_ms = max(
            0,
            int(
                (now - job.started_at).total_seconds() * 1000
            ),
        )

    if job.retry_count < job.max_retries:
        job.retry_count += 1
        job.status = "Pending"
        job.last_retry_at = now

        delay = min(
            RETRY_BASE_DELAY_SECONDS * (2 ** (job.retry_count - 1)),
            MAX_RETRY_DELAY_SECONDS,
        )

        job.next_retry_at = now + timedelta(seconds=delay)
        job.started_at = None
    else:
        job.status = "Failed"
        job.next_retry_at = None

    db.commit()
    db.refresh(job)

    return job


def recover_stuck_jobs(
    db: Session,
    timeout_minutes: int = JOB_TIMEOUT_MINUTES,
):
    now = utc_now()
    timeout_threshold = now - timedelta(minutes=timeout_minutes)

    stuck_jobs = (
        db.query(BackgroundJob)
        .filter(
            BackgroundJob.job_type.like("integration_sync:%"),
            BackgroundJob.status == "Running",
            BackgroundJob.started_at <= timeout_threshold,
        )
        .with_for_update(skip_locked=True)
        .all()
    )

    recovered_jobs = []

    for job in stuck_jobs:
        job.error_message = (
            "Job execution timed out. Job marked for recovery."
        )
        job.completed_at = now

        if job.started_at:
            job.duration_ms = max(
                0,
                int(
                    (now - job.started_at).total_seconds() * 1000
                ),
            )

        if job.retry_count < job.max_retries:
            job.retry_count += 1
            job.status = "Pending"
            job.last_retry_at = now

            delay = min(
                RETRY_BASE_DELAY_SECONDS * (2 ** (job.retry_count - 1)),
                MAX_RETRY_DELAY_SECONDS,
            )

            job.next_retry_at = now + timedelta(seconds=delay)
            job.started_at = None
        else:
            job.status = "Failed"
            job.next_retry_at = None

        recovered_jobs.append(job.id)

    db.commit()

    return recovered_jobs

def get_retryable_jobs(
    db: Session,
    limit: int = 20,
):
    now = utc_now()

    return (
        db.query(BackgroundJob)
        .filter(
            BackgroundJob.status == "Pending",
            BackgroundJob.retry_count > 0,
            BackgroundJob.next_retry_at <= now,
        )
        .order_by(BackgroundJob.next_retry_at.asc())
        .limit(limit)
        .all()
    )


def get_job(
    db: Session,
    job_id: int,
):
    return (
        db.query(BackgroundJob)
        .filter(BackgroundJob.id == job_id)
        .first()
    )