from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.integration_schedule import IntegrationSchedule

from app.services.integration_service import get_integration_by_id


def calculate_next_run(
    frequency,
    scheduled_time,
    timezone_name,
    day_of_week=None,
):
    try:
        schedule_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="Invalid timezone.",
        )

    now = datetime.now(schedule_timezone)

    candidate = datetime.combine(
        now.date(),
        scheduled_time,
        tzinfo=schedule_timezone,
    )

    if frequency == "daily":
        if candidate <= now:
            candidate += timedelta(days=1)

    elif frequency == "weekly":
        if day_of_week is None or not 0 <= day_of_week <= 6:
            raise HTTPException(
                status_code=400,
                detail="Weekly schedules require day_of_week between 0 and 6.",
            )

        days_ahead = (day_of_week - now.weekday()) % 7

        candidate = datetime.combine(
            now.date() + timedelta(days=days_ahead),
            scheduled_time,
            tzinfo=schedule_timezone,
        )

        if candidate <= now:
            candidate += timedelta(days=7)

    else:
        raise HTTPException(
            status_code=400,
            detail="Only daily and weekly schedules are currently supported.",
        )

    return candidate.astimezone(timezone.utc)


def validate_schedule_data(
    frequency,
    scheduled_time,
    timezone_name,
    day_of_week,
):
    if not scheduled_time:
        raise HTTPException(
            status_code=400,
            detail="Scheduled time is required.",
        )

    if frequency == "weekly":
        if day_of_week is None:
            raise HTTPException(
                status_code=400,
                detail="Select a day for weekly scheduling.",
            )

    elif frequency == "daily":
        day_of_week = None

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported schedule frequency.",
        )

    calculate_next_run(
        frequency,
        scheduled_time,
        timezone_name,
        day_of_week,
    )

    return day_of_week


def create_integration_schedule(
    db: Session,
    integration_id: int,
    company_id: int,
    schedule_data,
):
    integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    if integration.source_type not in {"csv", "rest_api"}:
        raise HTTPException(
            status_code=400,
            detail="Scheduling is currently supported only for CSV and REST API integrations.",
        )

    if integration.target_module != "products":
        raise HTTPException(
            status_code=400,
            detail="Only product integration scheduling is currently supported.",
        )

    existing = (
        db.query(IntegrationSchedule)
        .filter(
            IntegrationSchedule.integration_id == integration_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="A schedule already exists for this integration.",
        )

    data = schedule_data.model_dump()

    data["day_of_week"] = validate_schedule_data(
        data["frequency"],
        data["scheduled_time"],
        data["timezone"],
        data.get("day_of_week"),
    )

    next_run_at = calculate_next_run(
        data["frequency"],
        data["scheduled_time"],
        data["timezone"],
        data.get("day_of_week"),
    )

    schedule = IntegrationSchedule(
        integration_id=integration_id,
        frequency=data["frequency"],
        day_of_week=data["day_of_week"],
        scheduled_time=data["scheduled_time"],
        timezone=data["timezone"],
        is_active=data["is_active"],
        next_run_at=next_run_at,
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule

def get_integration_schedule(
    db: Session,
    integration_id: int,
    company_id: int,
):
    get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    schedule = (
        db.query(IntegrationSchedule)
        .filter(
            IntegrationSchedule.integration_id == integration_id,
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Integration schedule not found.",
        )

    return schedule


def update_integration_schedule(
    db: Session,
    integration_id: int,
    company_id: int,
    schedule_data,
):
    schedule = get_integration_schedule(
        db,
        integration_id,
        company_id,
    )

    data = schedule_data.model_dump(
        exclude_unset=True,
    )

    frequency = data.get(
        "frequency",
        schedule.frequency,
    )

    scheduled_time = data.get(
        "scheduled_time",
        schedule.scheduled_time,
    )

    timezone_name = data.get(
        "timezone",
        schedule.timezone,
    )

    day_of_week = data.get(
        "day_of_week",
        schedule.day_of_week,
    )

    day_of_week = validate_schedule_data(
        frequency,
        scheduled_time,
        timezone_name,
        day_of_week,
    )

    next_run_at = calculate_next_run(
        frequency,
        scheduled_time,
        timezone_name,
        day_of_week,
    )

    schedule.frequency = frequency
    schedule.scheduled_time = scheduled_time
    schedule.timezone = timezone_name
    schedule.day_of_week = day_of_week
    schedule.next_run_at = next_run_at

    if "is_active" in data:
        schedule.is_active = data["is_active"]

    db.commit()
    db.refresh(schedule)

    return schedule


def delete_integration_schedule(
    db: Session,
    integration_id: int,
    company_id: int,
):
    schedule = get_integration_schedule(
        db,
        integration_id,
        company_id,
    )

    db.delete(schedule)
    db.commit()

    return {
        "message": "Integration schedule deleted successfully.",
        "integration_id": integration_id,
    }