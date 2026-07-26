from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.services.notification_service import (
    get_notifications,
    create_notification,
    get_unread_count,
    mark_as_read,
    mark_all_as_read,
    delete_notification,
)
from app.schemas.notification_schema import NotificationCreate
router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("/")
def fetch_notifications(db: Session = Depends(get_db)):
    return get_notifications(db)


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db)):
    return {"count": get_unread_count(db)}


@router.post("/")
def add_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
):
    return create_notification(
        db,
        data.title,
        data.message,
        data.type,
    )


@router.put("/{notification_id}/read")
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
):
    notification = mark_as_read(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.put("/read-all")
def read_all(db: Session = Depends(get_db)):
    return mark_all_as_read(db)


@router.delete("/{notification_id}")
def remove_notification(
    notification_id: int,
    db: Session = Depends(get_db),
):
    notification = delete_notification(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Notification deleted"}