from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.schemas.audit_schema import (
    AuditLogResponse,
    AuditLogListResponse,
)
from app.services.audit_service import (
    get_audit_logs,
    get_audit_log_by_id,
)
from app.security.role_dependency import require_company_admin


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "/",
    response_model=AuditLogListResponse,
)
def read_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),

    search: str | None = Query(None),

    user_id: int | None = Query(None, ge=1),

    action: str | None = Query(None),

    module: str | None = Query(None),

    resource_type: str | None = Query(None),

    status: str | None = Query(None),

    date_from: datetime | None = Query(None),

    date_to: datetime | None = Query(None),

    sort_order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
    ),

    current_user: User = Depends(
        require_company_admin
    ),

    db: Session = Depends(get_db),
):
    return get_audit_logs(
        db=db,
        company_id=current_user.company_id,
        page=page,
        limit=limit,
        search=search,
        user_id=user_id,
        action=action,
        module=module,
        resource_type=resource_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort_order=sort_order,
    )


@router.get(
    "/{audit_log_id}",
    response_model=AuditLogResponse,
)
def read_audit_log(
    audit_log_id: int,

    current_user: User = Depends(
        require_company_admin
    ),

    db: Session = Depends(get_db),
):
    audit_log = get_audit_log_by_id(
        db=db,
        company_id=current_user.company_id,
        audit_log_id=audit_log_id,
    )

    if not audit_log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found.",
        )

    return audit_log