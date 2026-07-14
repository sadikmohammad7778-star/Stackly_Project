from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    module: str,
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        module=module
    )

    db.add(log)
    db.commit()