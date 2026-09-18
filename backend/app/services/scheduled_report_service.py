from datetime import datetime
from sqlalchemy.orm import Session

from app.models.scheduled_report import ScheduledReport


def create_scheduled_report(
    db: Session,
    company_id: int,
    user_id: int,
    data
):
    scheduled_report = ScheduledReport(
        company_id=company_id,
        created_by=user_id,
        report_type=data.report_type,
        filters=data.filters,
        frequency=data.frequency,
        execution_time=data.execution_time,
        recipients=data.recipients,
        format=data.format,
        is_active=data.is_active
    )

    db.add(scheduled_report)
    db.commit()
    db.refresh(scheduled_report)

    return scheduled_report


def get_scheduled_reports(
    db: Session,
    company_id: int
):
    return (
        db.query(ScheduledReport)
        .filter(ScheduledReport.company_id == company_id)
        .order_by(ScheduledReport.created_at.desc())
        .all()
    )


def get_scheduled_report(
    db: Session,
    company_id: int,
    scheduled_report_id: int
):
    return (
        db.query(ScheduledReport)
        .filter(
            ScheduledReport.id == scheduled_report_id,
            ScheduledReport.company_id == company_id
        )
        .first()
    )


def update_scheduled_report(
    db: Session,
    company_id: int,
    scheduled_report_id: int,
    data
):
    scheduled_report = get_scheduled_report(
        db,
        company_id,
        scheduled_report_id
    )

    if not scheduled_report:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(scheduled_report, field, value)

    scheduled_report.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(scheduled_report)

    return scheduled_report


def toggle_scheduled_report(
    db: Session,
    company_id: int,
    scheduled_report_id: int
):
    scheduled_report = get_scheduled_report(
        db,
        company_id,
        scheduled_report_id
    )

    if not scheduled_report:
        return None

    scheduled_report.is_active = not scheduled_report.is_active
    scheduled_report.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(scheduled_report)

    return scheduled_report


def delete_scheduled_report(
    db: Session,
    company_id: int,
    scheduled_report_id: int
):
    scheduled_report = get_scheduled_report(
        db,
        company_id,
        scheduled_report_id
    )

    if not scheduled_report:
        return None

    db.delete(scheduled_report)
    db.commit()

    return True