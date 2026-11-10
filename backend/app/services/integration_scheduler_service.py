import time
import logging

from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config.database import SessionLocal

from app.models.integration_schedule import IntegrationSchedule
from app.models.integration import Integration
from app.models.background_job import BackgroundJob

from app.services.integration_schedule_service import calculate_next_run
from app.services.integration_sync_service import synchronize_products

from app.services.background_job_service import (
    complete_job,
    fail_job,
    recover_stuck_jobs,
)


logger = logging.getLogger(__name__)

POLL_INTERVAL = 30
MAX_JOBS_PER_CYCLE = 20


def claim_due_schedules(db: Session):
    now = datetime.now(timezone.utc)

    schedules = (
        db.query(IntegrationSchedule)
        .filter(
            IntegrationSchedule.is_active.is_(True),
            IntegrationSchedule.next_run_at <= now,
        )
        .order_by(IntegrationSchedule.next_run_at.asc())
        .with_for_update(skip_locked=True)
        .limit(MAX_JOBS_PER_CYCLE)
        .all()
    )

    claimed = 0

    for schedule in schedules:
        integration = (
            db.query(Integration)
            .filter(
                Integration.id == schedule.integration_id,
            )
            .first()
        )

        if not integration or not integration.is_enabled:
            schedule.last_run_status = "Skipped"

            schedule.next_run_at = calculate_next_run(
                schedule.frequency,
                schedule.scheduled_time,
                schedule.timezone,
                schedule.day_of_week,
            )

            continue

        job = BackgroundJob(
            company_id=integration.company_id,
            triggered_by=integration.created_by,
            job_type=f"integration_sync:{schedule.id}",
            status="Pending",
            retry_count=0,
            max_retries=3,
        )

        db.add(job)

        schedule.next_run_at = calculate_next_run(
            schedule.frequency,
            schedule.scheduled_time,
            schedule.timezone,
            schedule.day_of_week,
        )

        schedule.last_run_status = "Pending"

        claimed += 1

    db.commit()

    if claimed:
        logger.info("Created %s scheduled integration jobs", claimed)

    return claimed


def claim_pending_job(db: Session, job_id: int):
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    result = (
        db.query(BackgroundJob)
        .filter(
            BackgroundJob.id == job_id,
            BackgroundJob.status == "Pending",
            or_(
                BackgroundJob.next_retry_at.is_(None),
                BackgroundJob.next_retry_at <= now,
            ),
        )
        .update(
            {
                BackgroundJob.status: "Running",
                BackgroundJob.started_at: now,
                BackgroundJob.completed_at: None,
            },
            synchronize_session=False,
        )
    )

    db.commit()

    return result == 1


def execute_integration_job(
    db: Session,
    job_type: str,
    company_id: int,
    triggered_by: int,
):
    schedule_id = int(job_type.split(":")[1])

    schedule = (
        db.query(IntegrationSchedule)
        .filter(
            IntegrationSchedule.id == schedule_id,
        )
        .with_for_update()
        .first()
    )

    if not schedule:
        raise ValueError("Integration schedule not found.")

    integration = (
        db.query(Integration)
        .filter(
            Integration.id == schedule.integration_id,
            Integration.company_id == company_id,
        )
        .first()
    )

    if not integration:
        raise ValueError("Integration not found.")

    if not integration.is_enabled:
        raise ValueError("Integration is disabled.")

    result = synchronize_products(
        db=db,
        integration_id=integration.id,
        company_id=integration.company_id,
        user_id=triggered_by or integration.created_by,
        trigger_type="scheduled",
    )

    schedule.last_run_at = datetime.now(timezone.utc)
    schedule.last_run_status = result["status"].capitalize()

    db.commit()

    if result["status"] not in {"completed", "success"}:
        raise RuntimeError(
            result.get("error_summary")
            or "Scheduled synchronization failed."
        )

    return result


def process_pending_jobs(db: Session):
    now =datetime.now(timezone.utc).replace(tzinfo=None)

    jobs = (
        db.query(BackgroundJob)
        .filter(
            BackgroundJob.job_type.like("integration_sync:%"),
            BackgroundJob.status == "Pending",
            or_(
                BackgroundJob.next_retry_at.is_(None),
                BackgroundJob.next_retry_at <= now,
            ),
        )
        .order_by(BackgroundJob.created_at.asc())
        .limit(MAX_JOBS_PER_CYCLE)
        .all()
    )

    for job in jobs:
        job_id = job.id
        job_type = job.job_type
        company_id = job.company_id
        triggered_by = job.triggered_by

        if not claim_pending_job(db, job_id):
            continue

        try:
            result = execute_integration_job(
                db=db,
                job_type=job_type,
                company_id=company_id,
                triggered_by=triggered_by,
            )

            complete_job(db, job_id)

            logger.info(
                "Integration job %s completed with status %s",
                job_id,
                result["status"],
            )

        except Exception as exc:
            db.rollback()

            try:
                schedule_id = int(job_type.split(":")[1])

                schedule = (
                    db.query(IntegrationSchedule)
                    .filter(
                        IntegrationSchedule.id == schedule_id,
                    )
                    .first()
                )

                if schedule:
                    schedule.last_run_at = datetime.now(timezone.utc)
                    schedule.last_run_status = "Failed"

                    db.commit()

            except Exception:
                db.rollback()

                logger.exception(
                    "Failed to update schedule status for job %s",
                    job_id,
                )

            failed_job = fail_job(
                db,
                job_id,
                str(exc),
            )

            if failed_job and failed_job.status == "Pending":
                logger.warning(
                    "Integration job %s scheduled for retry %s/%s at %s",
                    job_id,
                    failed_job.retry_count,
                    failed_job.max_retries,
                    failed_job.next_retry_at,
                )
            else:
                logger.error(
                    "Integration job %s permanently failed",
                    job_id,
                )

            logger.exception(
                "Integration job %s execution failed",
                job_id,
            )


def run_scheduler_cycle():
    db = SessionLocal()

    try:
        recovered_jobs = recover_stuck_jobs(db)

        if recovered_jobs:
            logger.warning(
                "Recovered stuck integration jobs: %s",
                recovered_jobs,
            )

        claim_due_schedules(db)
        process_pending_jobs(db)

    except Exception:
        db.rollback()
        logger.exception("Integration scheduler cycle failed")

    finally:
        db.close()


def integration_scheduler_worker():
    logger.info("Integration scheduler worker started")

    while True:
        try:
            run_scheduler_cycle()

        except Exception:
            logger.exception(
                "Unexpected integration scheduler worker error"
            )

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    integration_scheduler_worker()