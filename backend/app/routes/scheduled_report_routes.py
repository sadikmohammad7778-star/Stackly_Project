from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User

from app.schemas.report_schema import (
    ScheduledReportCreate,
    ScheduledReportUpdate,
    ScheduledReportResponse
)

from app.services.scheduled_report_service import (
    create_scheduled_report,
    get_scheduled_reports,
    get_scheduled_report,
    update_scheduled_report,
    toggle_scheduled_report,
    delete_scheduled_report
)


router = APIRouter(
    prefix="/scheduled-reports",
    tags=["Scheduled Reports"]
)


@router.post(
    "",
    response_model=ScheduledReportResponse
)
def create_report_schedule(
    data: ScheduledReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_scheduled_report(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        data=data
    )


@router.get(
    "",
    response_model=list[ScheduledReportResponse]
)
def list_report_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_scheduled_reports(
        db=db,
        company_id=current_user.company_id
    )


@router.get(
    "/{scheduled_report_id}",
    response_model=ScheduledReportResponse
)
def get_report_schedule(
    scheduled_report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scheduled_report = get_scheduled_report(
        db=db,
        company_id=current_user.company_id,
        scheduled_report_id=scheduled_report_id
    )

    if not scheduled_report:
        raise HTTPException(
            status_code=404,
            detail="Scheduled report not found"
        )

    return scheduled_report


@router.put(
    "/{scheduled_report_id}",
    response_model=ScheduledReportResponse
)
def update_report_schedule(
    scheduled_report_id: int,
    data: ScheduledReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scheduled_report = update_scheduled_report(
        db=db,
        company_id=current_user.company_id,
        scheduled_report_id=scheduled_report_id,
        data=data
    )

    if not scheduled_report:
        raise HTTPException(
            status_code=404,
            detail="Scheduled report not found"
        )

    return scheduled_report


@router.patch(
    "/{scheduled_report_id}/toggle",
    response_model=ScheduledReportResponse
)
def toggle_report_schedule(
    scheduled_report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scheduled_report = toggle_scheduled_report(
        db=db,
        company_id=current_user.company_id,
        scheduled_report_id=scheduled_report_id
    )

    if not scheduled_report:
        raise HTTPException(
            status_code=404,
            detail="Scheduled report not found"
        )

    return scheduled_report


@router.delete(
    "/{scheduled_report_id}"
)
def delete_report_schedule(
    scheduled_report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = delete_scheduled_report(
        db=db,
        company_id=current_user.company_id,
        scheduled_report_id=scheduled_report_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Scheduled report not found"
        )

    return {
        "message": "Scheduled report deleted successfully"
    }