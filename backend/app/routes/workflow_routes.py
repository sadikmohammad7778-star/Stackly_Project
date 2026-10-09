from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User

from app.models.approval_history import ApprovalHistory
from app.models.workflow_config import WorkflowConfiguration

from app.schemas.approval_request_schema import (
    ApprovalRequestCreate,
    ApprovalRequestResponse,
    ApprovalRequestSubmit,
    ApprovalRequestApprove,
    ApprovalRequestReject,
    ApprovalRequestCancel,
)

from app.schemas.approval_history_schema import (
    ApprovalHistoryResponse,
)

from app.schemas.workflow_config_schema import (
    WorkflowConfigurationCreate,
    WorkflowConfigurationUpdate,
    WorkflowConfigurationResponse,
)

from app.services.workflow_service import (
    create_approval_request,
    get_approval_request,
    get_approval_requests,
    get_my_requests,
    get_pending_requests,
    get_approval_history,
    cancel_approval_request,
    get_pending_count,
)

from app.services.workflow_config_service import (
    create_workflow_configuration,
    get_workflow_configurations,
    get_workflow_configuration,
    update_workflow_configuration,
)

from app.services.approval_service import (
    approve_request,
    reject_approval_request,
)

router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
)


@router.post(
    "/requests",
    response_model=ApprovalRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request(
    request_data: ApprovalRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_approval_request(
        db=db,
        request_data=request_data,
        current_user=current_user,
    )


@router.post(
    "/requests/{request_id}/submit",
    response_model=ApprovalRequestResponse,
)
def submit_request(
    request_id: int,
    request_data: ApprovalRequestSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = get_approval_request(
        db=db,
        request_id=request_id,
        current_user=current_user,
    )

    if request.requested_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only submit your own request.",
        )

    if request.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft requests can be submitted.",
        )

    workflow_config = (
        db.query(WorkflowConfiguration)
        .filter(
            WorkflowConfiguration.company_id == current_user.company_id,
            WorkflowConfiguration.request_type == request.request_type,
            WorkflowConfiguration.is_active == True,
        )
        .first()
    )

    if not workflow_config:
        raise HTTPException(
            status_code=400,
            detail="No active workflow configuration found for this request type.",
        )

    request.submitted_at = datetime.now(timezone.utc)

    if workflow_config.approval_required:
        request.status = "pending_approval"
        to_status = "pending_approval"
    else:
        request.status = "approved"
        request.completed_at = datetime.now(timezone.utc)
        to_status = "approved"

    history = ApprovalHistory(
        approval_request_id=request.id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="REQUEST_SUBMITTED",
        from_status="draft",
        to_status=to_status,
        comments=request_data.comments,
        action_metadata={
            "approval_required": workflow_config.approval_required,
        },
    )

    db.add(history)
    db.commit()
    db.refresh(request)

    return request

@router.get(
    "/requests",
)
def list_requests(
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    request_type: str | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_approval_requests(
        db=db,
        current_user=current_user,
        status_filter=status_filter,
        request_type=request_type,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/my-requests",
)
def my_requests(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_requests(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/pending",
)
def pending_requests(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_pending_requests(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/pending-count",
)
def pending_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = get_pending_count(
        db=db,
        current_user=current_user,
    )

    return {
        "pending_count": count
    }


@router.get(
    "/requests/{request_id}",
    response_model=ApprovalRequestResponse,
)
def request_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_approval_request(
        db=db,
        request_id=request_id,
        current_user=current_user,
    )


@router.get(
    "/requests/{request_id}/history",
    response_model=list[ApprovalHistoryResponse],
)
def request_history(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_approval_history(
        db=db,
        request_id=request_id,
        current_user=current_user,
    )


@router.post(
    "/requests/{request_id}/approve",
    response_model=ApprovalRequestResponse,
)
def approve(
    request_id: int,
    request_data: ApprovalRequestApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return approve_request(
        db=db,
        request_id=request_id,
        current_user=current_user,
        comments=request_data.comments,
    )


@router.post(
    "/requests/{request_id}/reject",
    response_model=ApprovalRequestResponse,
)
def reject(
    request_id: int,
    request_data: ApprovalRequestReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return reject_approval_request(
        db=db,
        request_id=request_id,
        current_user=current_user,
        comments=request_data.comments,
    )


@router.post(
    "/requests/{request_id}/cancel",
    response_model=ApprovalRequestResponse,
)
def cancel(
    request_id: int,
    request_data: ApprovalRequestCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cancel_approval_request(
        db=db,
        request_id=request_id,
        current_user=current_user,
        comments=request_data.comments,
    )



@router.post(
    "/configurations",
    response_model=WorkflowConfigurationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_configuration(
    config_data: WorkflowConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_workflow_configuration(
        db=db,
        config_data=config_data,
        current_user=current_user,
    )


@router.get(
    "/configurations",
    response_model=list[WorkflowConfigurationResponse],
)
def list_configurations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_workflow_configurations(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/configurations/{config_id}",
    response_model=WorkflowConfigurationResponse,
)
def configuration_details(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_workflow_configuration(
        db=db,
        config_id=config_id,
        current_user=current_user,
    )


@router.put(
    "/configurations/{config_id}",
    response_model=WorkflowConfigurationResponse,
)
def update_configuration(
    config_id: int,
    config_data: WorkflowConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_workflow_configuration(
        db=db,
        config_id=config_id,
        config_data=config_data,
        current_user=current_user,
    )