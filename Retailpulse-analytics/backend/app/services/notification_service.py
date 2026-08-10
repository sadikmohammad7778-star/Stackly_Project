from sqlalchemy.orm import Session

from app.models.notification import Notification


# ============================================================
# Create Notification
# ============================================================

def create_notification(
    db: Session,
    title: str,
    message: str,
    type: str,
):
    notification = Notification(
        title=title,
        message=message,
        type=type,
    )

    db.add(notification)

    # The calling service controls commit/rollback.
    db.flush()

    return notification


# ============================================================
# Get Notifications
# ============================================================

def get_notifications(
    db: Session,
):
    return (
        db.query(Notification)
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )


# ============================================================
# Get Unread Count
# ============================================================

def get_unread_count(
    db: Session,
):
    return (
        db.query(Notification)
        .filter(
            Notification.is_read == False
        )
        .count()
    )


# ============================================================
# Mark Notification As Read
# ============================================================

def mark_as_read(
    db: Session,
    notification_id: int,
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if notification:
        notification.is_read = True

        db.commit()
        db.refresh(notification)

    return notification


# ============================================================
# Mark All Notifications As Read
# ============================================================

def mark_all_as_read(
    db: Session,
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.is_read == False
        )
        .all()
    )

    for notification in notifications:
        notification.is_read = True

    db.commit()

    return {
        "message": "All notifications marked as read"
    }


# ============================================================
# Delete Notification
# ============================================================

def delete_notification(
    db: Session,
    notification_id: int,
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if notification:
        db.delete(notification)
        db.commit()

    return notification