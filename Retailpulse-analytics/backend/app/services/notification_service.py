from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.services.audit_service import create_audit_log


def create_notification(db: Session, title: str, message: str, type: str):
    notification = Notification(
        title=title,
        message=message,
        type=type,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notifications(db: Session):
    return (
        db.query(Notification)
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_unread_count(db: Session):
    return (
        db.query(Notification)
        .filter(Notification.is_read == False)
        .count()
    )


def mark_as_read(
    db: Session,
    notification_id: int,
    user_id: int,
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)

        create_audit_log(
            db=db,
            user_id=user_id,
            action="UPDATE",
            module="Notification",
        )

    return notification

def mark_all_as_read(
    db: Session,
    user_id: int,
):
    notifications = (
        db.query(Notification)
        .filter(Notification.is_read == False)
        .all()
    )

    for notification in notifications:
        notification.is_read = True

    db.commit()

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        module="Notification",
    )

    return {"message": "All notifications marked as read"}


def delete_notification(
    db: Session,
    notification_id: int,
    user_id: int,
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if notification:
        db.delete(notification)
        db.commit()

        create_audit_log(
            db=db,
            user_id=user_id,
            action="DELETE",
            module="Notification",
        )

    return notification