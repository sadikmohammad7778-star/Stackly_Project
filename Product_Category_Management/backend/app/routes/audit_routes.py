from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"]
)


@router.get("/")
def get_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).all()