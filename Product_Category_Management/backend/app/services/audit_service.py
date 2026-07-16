from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    company_id: int,
    entity_name: str,
    action: str,
    performed_by: str
):
    log = AuditLog(
        company_id=company_id,
        entity_name=entity_name,
        action=action,
        performed_by=performed_by
    )

    db.add(log)
    db.commit()