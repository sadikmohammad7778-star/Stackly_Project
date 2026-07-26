from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.audit_schema import AuditLogResponse
from app.services.audit_service import get_audit_logs

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("/", response_model=list[AuditLogResponse])
def read_audit_logs(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_audit_logs(
        db=db,
        company_id=company_id,
    )