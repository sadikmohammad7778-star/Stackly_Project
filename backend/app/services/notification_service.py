from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User

IST = ZoneInfo("Asia/Kolkata")

ROLE_NOTIFICATION_TYPES = {
    "Super Admin": {
        "STOCKOUT_RISK",
        "LOW_STOCK",
        "OVERSTOCK",
        "SALES_ALERT",
        "IMPORT_COMPLETED",
        "IMPORT_FAILED",
        "SYSTEM_ALERT",
    },
    "Company Admin": {
        "STOCKOUT_RISK",
        "LOW_STOCK",
        "OVERSTOCK",
        "SALES_ALERT",
        "IMPORT_COMPLETED",
        "IMPORT_FAILED",
        "SYSTEM_ALERT",
    },
    "Analyst": {
        "STOCKOUT_RISK",
        "LOW_STOCK",
        "OVERSTOCK",
        "SALES_ALERT",
    },
    "Viewer": {
        "STOCKOUT_RISK",
        "LOW_STOCK",
        "OVERSTOCK",
    },
}


class NotificationService:

    @staticmethod
    def can_receive_notification(
        db: Session,
        user_id: int,
        notification_type: str,
    ) -> bool:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return False

        allowed_types = ROLE_NOTIFICATION_TYPES.get(
            user.role,
            set(),
        )

        return notification_type in allowed_types

    @staticmethod
    def create_notification(
        db: Session,
        *,
        company_id: int,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        priority: str = "LOW",
        resource_type: str | None = None,
        resource_id: int | None = None,
        dedupe_key: str | None = None,
        expires_at: datetime | None = None,
    ) -> Notification | None:

        user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.company_id == company_id,
            )
            .first()
        )

        if not user:
            return None

        if not NotificationService.can_receive_notification(
            db=db,
            user_id=user_id,
            notification_type=notification_type,
        ):
            return None

        if dedupe_key:
            existing = (
                db.query(Notification)
                .filter(
                    Notification.company_id == company_id,
                    Notification.user_id == user_id,
                    Notification.dedupe_key == dedupe_key,
                    Notification.resolved_at.is_(None),
                )
                .first()
            )

            if existing:
                return existing

        notification = Notification(
            company_id=company_id,
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            resource_type=resource_type,
            resource_id=resource_id,
            is_read=False,
            dedupe_key=dedupe_key,
            expires_at=expires_at,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def get_notifications(
        db: Session,
        *,
        company_id: int,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        is_read: bool | None = None,
        notification_type: str | None = None,
        priority: str | None = None,
    ):

        query = (
            db.query(Notification)
            .filter(
                Notification.company_id == company_id,
                Notification.user_id == user_id,
            )
        )

        if is_read is not None:
            query = query.filter(
                Notification.is_read == is_read
            )

        if notification_type:
            query = query.filter(
                Notification.type == notification_type
            )

        if priority:
            query = query.filter(
                Notification.priority == priority
            )

        now = datetime.now(IST)

        query = query.filter(
            (Notification.expires_at.is_(None))
            | (Notification.expires_at > now)
        )

        total = query.count()

        unread_count = (
            db.query(func.count(Notification.id))
            .filter(
                Notification.company_id == company_id,
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
                (
                    (Notification.expires_at.is_(None))
                    | (Notification.expires_at > now)
                ),
            )
            .scalar()
            or 0
        )

        offset = (page - 1) * page_size

        notifications = (
            query
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {
            "items": notifications,
            "total": total,
            "page": page,
            "page_size": page_size,
            "unread_count": unread_count,
        }

    @staticmethod
    def get_unread_count(
        db: Session,
        *,
        company_id: int,
        user_id: int,
    ):

        now = datetime.now(IST)

        return (
            db.query(func.count(Notification.id))
            .filter(
                Notification.company_id == company_id,
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
                (
                    (Notification.expires_at.is_(None))
                    | (Notification.expires_at > now)
                ),
            )
            .scalar()
            or 0
        )

    @staticmethod
    def mark_as_read(
        db: Session,
        *,
        notification_id: int,
        company_id: int,
        user_id: int,
    ):

        notification = (
            db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.company_id == company_id,
                Notification.user_id == user_id,
            )
            .first()
        )

        if not notification:
            return None

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(IST)

            db.commit()
            db.refresh(notification)

        return notification

    @staticmethod
    def mark_all_as_read(
        db: Session,
        *,
        company_id: int,
        user_id: int,
    ):

        notifications = (
            db.query(Notification)
            .filter(
                Notification.company_id == company_id,
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .all()
        )

        if not notifications:
            return 0

        now = datetime.now(IST)

        for notification in notifications:
            notification.is_read = True
            notification.read_at = now

        db.commit()

        return len(notifications)

    @staticmethod
    def resolve_notification(
        db: Session,
        *,
        company_id: int,
        user_id: int,
        dedupe_key: str,
    ):

        notifications = (
            db.query(Notification)
            .filter(
                Notification.company_id == company_id,
                Notification.user_id == user_id,
                Notification.dedupe_key == dedupe_key,
                Notification.resolved_at.is_(None),
            )
            .all()
        )

        if not notifications:
            return 0

        now = datetime.now(IST)

        for notification in notifications:
            notification.resolved_at = now

        db.commit()

        return len(notifications)


def create_notification(
    db: Session,
    company_id: int,
    user_id: int,
    type: str,
    title: str,
    message: str,
    priority: str = "LOW",
    resource_type: str | None = None,
    resource_id: int | None = None,
    dedupe_key: str | None = None,
    expires_at: datetime | None = None,
):
    return NotificationService.create_notification(
        db=db,
        company_id=company_id,
        user_id=user_id,
        notification_type=type,
        title=title,
        message=message,
        priority=priority,
        resource_type=resource_type,
        resource_id=resource_id,
        dedupe_key=dedupe_key,
        expires_at=expires_at,
    )