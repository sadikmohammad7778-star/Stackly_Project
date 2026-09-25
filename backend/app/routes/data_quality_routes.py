from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.config.dependency import (
    get_db,
    get_current_user,
    require_data_quality_admin,
)
from app.models.user import User
from app.schemas.data_quality_schema import DataQualityIssueUpdate
from app.services.data_quality_service import DataQualityService


router = APIRouter(
    prefix="/data-quality",
    tags=["Data Quality"],
)


@router.post("/reconcile/inventory")
def reconcile_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_data_quality_admin),
):
    return DataQualityService.run_inventory_reconciliation(
        db=db,
        company_id=current_user.company_id,
        triggered_by=current_user.id,
    )

@router.get("/reconciliation/history")
def get_reconciliation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DataQualityService.get_reconciliation_history(
        db=db,
        company_id=current_user.company_id,
    )


@router.get("/issues")
def get_data_quality_issues(
    status: str = None,
    severity: str = None,
    issue_type: str = None,
    module: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DataQualityService.get_data_quality_issues(
        db=db,
        company_id=current_user.company_id,
        status=status,
        severity=severity,
        issue_type=issue_type,
        module=module,
        search=search,
    )

@router.get("/issues/{issue_id}")
def get_data_quality_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DataQualityService.get_data_quality_issue(
        db=db,
        company_id=current_user.company_id,
        issue_id=issue_id,
    )

@router.patch("/issues/{issue_id}")
def update_data_quality_issue(
    issue_id: int,
    data: DataQualityIssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_data_quality_admin),
):
    return DataQualityService.update_data_quality_issue(
        db=db,
        company_id=current_user.company_id,
        issue_id=issue_id,
        status=data.status,
        resolution_note=data.resolution_note,
        resolved_by=current_user.id,
    )

@router.get("/dashboard")
def get_data_quality_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DataQualityService.get_data_quality_dashboard(
        db=db,
        company_id=current_user.company_id,
    )