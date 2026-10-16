from datetime import datetime

from sqlalchemy.orm import Session

from app.models.background_job import BackgroundJob


def create_job(
    db: Session,
    job_type: str,
    company_id: int = None,
    triggered_by: int = None,
):
    job = BackgroundJob(
        job_type=job_type,
        company_id=company_id,
        triggered_by=triggered_by,
        status="Pending",
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

    job.status = "Running"
    job.started_at = datetime.utcnow()

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

    job.completed_at = datetime.utcnow()
    job.status = "Completed"

    if job.started_at:
        job.duration_ms = max(
            0,
            int(
                (
                    job.completed_at - job.started_at
                ).total_seconds() * 1000
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

    job.completed_at = datetime.utcnow()
    job.status = "Failed"
    job.error_message = error_message[:2000]

    if job.started_at:
        job.duration_ms = max(
            0,
            int(
                (
                    job.completed_at - job.started_at
                ).total_seconds() * 1000
            ),
        )

    db.commit()
    db.refresh(job)

    return job