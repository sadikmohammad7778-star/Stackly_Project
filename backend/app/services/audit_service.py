from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.notification import Notification

IST = ZoneInfo("Asia/Kolkata")

SYSTEM_ALERT_ACTIONS = {
    "CREATE",
    "UPDATE",
    "DELETE",
    "STOCK_IN",
    "STOCK_OUT",
    "ADJUST",
}

SYSTEM_ALERT_MODULES = {
    "Inventory",
    "Sales",
    "Data Import",
    "Company",
    "User",
    "Employee",
}

SYSTEM_ALERT_ROLES = {
    "Super Admin",
    "Company Admin",
}


def create_audit_log(
    db: Session,
    company_id: int,
    user_id: int,
    module: str,
    action: str,
    description: str,
    ip_address: str = None,
    browser: str = None,
    resource_type: str = None,
    resource_id: str = None,
    before_values: dict = None,
    after_values: dict = None,
    status: str = "SUCCESS",
    user_agent: str = None,
):
    log = AuditLog(
        company_id=company_id,
        user_id=user_id,
        module=module,
        action=action,
        description=description,
        ip_address=ip_address,
        browser=browser,
        resource_type=resource_type,
        resource_id=resource_id,
        before_values=before_values,
        after_values=after_values,
        status=status,
        user_agent=user_agent,
    )

    db.add(log)
    db.flush()

    if (
        status == "SUCCESS"
        and action in SYSTEM_ALERT_ACTIONS
        and module in SYSTEM_ALERT_MODULES
    ):
        users = (
            db.query(User)
            .filter(
                User.company_id == company_id,
                User.role.in_(SYSTEM_ALERT_ROLES),
                User.status.is_(True),
            )
            .all()
        )

        for user in users:
            dedupe_key = f"audit:{log.id}:system-alert:{user.id}"

            existing = (
                db.query(Notification)
                .filter(
                    Notification.company_id == company_id,
                    Notification.user_id == user.id,
                    Notification.dedupe_key == dedupe_key,
                )
                .first()
            )

            if existing:
                continue

            notification = Notification(
                company_id=company_id,
                user_id=user.id,
                type="SYSTEM_ALERT",
                title="System Activity",
                message=description,
                priority="LOW",
                resource_type=resource_type,
                resource_id=int(resource_id)
                if resource_id and str(resource_id).isdigit()
                else None,
                is_read=False,
                created_at=datetime.now(IST),
                dedupe_key=dedupe_key,
            )

            db.add(notification)

    db.flush()

    return log


def get_audit_logs(
    db: Session,
    company_id: int,
    page: int = 1,
    limit: int = 25,
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    module: Optional[str] = None,
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_order: str = "desc",
):
    query = (
        db.query(AuditLog)
        .join(
            User,
            AuditLog.user_id == User.id,
        )
        .filter(
            AuditLog.company_id == company_id
        )
    )

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                User.name.ilike(search_pattern),
                AuditLog.action.ilike(search_pattern),
                AuditLog.module.ilike(search_pattern),
                AuditLog.resource_type.ilike(search_pattern),
                AuditLog.resource_id.ilike(search_pattern),
                AuditLog.description.ilike(search_pattern),
            )
        )

    if user_id is not None:
        query = query.filter(
            AuditLog.user_id == user_id
        )

    if action:
        query = query.filter(
            AuditLog.action == action
        )

    if module:
        query = query.filter(
            AuditLog.module == module
        )

    if resource_type:
        query = query.filter(
            AuditLog.resource_type == resource_type
        )

    if status:
        query = query.filter(
            AuditLog.status == status
        )

    if date_from:
        query = query.filter(
            AuditLog.created_at >= date_from
        )

    if date_to:
        query = query.filter(
            AuditLog.created_at <= date_to
        )

    total = query.count()

    total_creates = query.filter(
        AuditLog.action.in_(["CREATE", "STOCK_IN"])
    ).count()

    total_updates = query.filter(
        AuditLog.action.in_(["UPDATE", "ADJUST"])
    ).count()

    total_deletes = query.filter(
        AuditLog.action.in_(["DELETE", "STOCK_OUT"])
    ).count()

    if sort_order.lower() == "asc":
        query = query.order_by(
            AuditLog.created_at.asc()
        )
    else:
        query = query.order_by(
            AuditLog.created_at.desc()
        )

    offset = (page - 1) * limit

    items = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_pages = (
        (total + limit - 1) // limit
        if total > 0
        else 0
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_creates": total_creates,
        "total_updates": total_updates,
        "total_deletes": total_deletes,
    }


def get_audit_log_by_id(
    db: Session,
    company_id: int,
    audit_log_id: int,
):
    return (
        db.query(AuditLog)
        .filter(
            AuditLog.id == audit_log_id,
            AuditLog.company_id == company_id,
        )
        .first()
    )