from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    module: str = None,  # Keep this so existing calls don't break
):
    log = AuditLog(
        user_id=user_id,
        action=action
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log