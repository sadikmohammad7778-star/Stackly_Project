from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    company_id: int,
    user_id: int,
    module: str,
    action: str,
    description: str,
    ip_address: str = None,
    browser: str = None,
):
    log = AuditLog(
        company_id=company_id,
        user_id=user_id,
        module=module,
        action=action,
        description=description,
        ip_address=ip_address,
        browser=browser,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_audit_logs(
    db: Session,
    company_id: int,
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.company_id == company_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )