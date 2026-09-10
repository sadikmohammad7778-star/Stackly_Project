from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.schemas.notification_schema import (
    NotificationListResponse,
    NotificationResponse,
)
from app.services.notification_service import NotificationService


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=NotificationListResponse,
)
def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_read: bool | None = None,
    notification_type: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return NotificationService.get_notifications(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        is_read=is_read,
        notification_type=notification_type,
        priority=priority,
    )


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    count = NotificationService.get_unread_count(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )

    return {
        "unread_count": count
    }


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    notification = NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    return notification


@router.patch("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated_count = NotificationService.mark_all_as_read(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )

    return {
        "message": "All notifications marked as read",
        "updated_count": updated_count,
    }