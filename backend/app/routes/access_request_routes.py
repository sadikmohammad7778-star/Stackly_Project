import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.models.user import User
from app.models.approval_request import ApprovalRequest
from app.models.approval_history import ApprovalHistory
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.audit_log import AuditLog
from app.schemas.access_request_schema import (
    AccessRequestCreate,
    AccessRequestReview,
    AccessRequestResponse,
)
from app.security.auth_dependency import get_current_user
from app.security.permission_dependency import require_permission


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/access-requests",
    tags=["Access Requests"],
)


def ensure_company_access(current_user: User):
    if current_user.company_id is None and current_user.role != "Super Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not associated with a company.",
        )


def ensure_access_request_access(
    request: ApprovalRequest,
    current_user: User,
):
    ensure_company_access(current_user)

    if current_user.role == "Super Admin":
        return

    if request.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found.",
        )


@router.post(
    "",
    response_model=AccessRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_access_request(
    payload: AccessRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_company_access(current_user)

    if current_user.role == "Super Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin does not need to request role permissions.",
        )

    if payload.priority not in {"low", "medium", "high"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Priority must be low, medium, or high.",
        )

    permission = (
        db.query(Permission)
        .filter(
            Permission.id == payload.permission_id,
            Permission.is_active.is_(True),
        )
        .first()
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found or inactive.",
        )

    existing_assignment = (
        db.query(RolePermission)
        .filter(
            RolePermission.company_id == current_user.company_id,
            RolePermission.role == current_user.role,
            RolePermission.permission_id == permission.id,
        )
        .first()
    )

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Your role already has this permission.",
        )

    existing_requests = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.company_id == current_user.company_id,
            ApprovalRequest.requested_by == current_user.id,
            ApprovalRequest.request_type == "access_request",
            ApprovalRequest.status.in_(["submitted", "pending"]),
        )
        .all()
    )

    for existing in existing_requests:
        changes = existing.requested_changes or {}

        if str(changes.get("permission_id")) == str(permission.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have a pending request for this permission.",
            )

    approver = (
        db.query(User)
        .filter(
            User.company_id == current_user.company_id,
            User.role == "Company Admin",
            User.status.is_(True),
            User.id != current_user.id,
        )
        .order_by(User.id.asc())
        .first()
    )

    now = datetime.now(timezone.utc)

    request = ApprovalRequest(
        company_id=current_user.company_id,
        request_type="access_request",
        requested_by=current_user.id,
        assigned_approver_id=approver.id if approver else None,
        related_entity_type="permission",
        related_entity_id=permission.id,
        requested_changes={
            "permission_id": permission.id,
            "permission_code": permission.code,
            "role": current_user.role,
            "requested_action": "grant",
        },
        reason=payload.reason,
        priority=payload.priority,
        status="pending",
        submitted_at=now,
    )

    try:
        db.add(request)
        db.flush()

        db.add(
            ApprovalHistory(
                approval_request_id=request.id,
                company_id=current_user.company_id,
                user_id=current_user.id,
                action="SUBMITTED",
                from_status="draft",
                to_status="pending",
                comments=payload.reason,
                action_metadata={
                    "permission_id": permission.id,
                    "permission_code": permission.code,
                },
            )
        )

        db.add(
            AuditLog(
                company_id=current_user.company_id,
                user_id=current_user.id,
                module="Data Governance",
                action="ACCESS_REQUEST_SUBMITTED",
                resource_type="ApprovalRequest",
                resource_id=request.id,
                description=f"Access requested for {permission.code}",
                after_values={
                    "permission_id": permission.id,
                    "status": "pending",
                },
                status="SUCCESS",
            )
        )

        db.commit()
        db.refresh(request)

        return request

    except Exception:
        db.rollback()
        logger.exception("Failed to submit an access request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit access request.",
        )


@router.get(
    "/mine",
    response_model=list[AccessRequestResponse],
)
def get_my_access_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_company_access(current_user)

    if current_user.role == "Super Admin":
        query = db.query(ApprovalRequest).filter(
            ApprovalRequest.requested_by == current_user.id,
            ApprovalRequest.request_type == "access_request",
        )
    else:
        query = db.query(ApprovalRequest).filter(
            ApprovalRequest.company_id == current_user.company_id,
            ApprovalRequest.requested_by == current_user.id,
            ApprovalRequest.request_type == "access_request",
        )

    return query.order_by(
        ApprovalRequest.created_at.desc()
    ).all()


@router.get(
    "/pending",
    response_model=list[AccessRequestResponse],
)
def get_pending_access_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("data_governance", "manage_access")
    ),
):
    ensure_company_access(current_user)

    query = db.query(ApprovalRequest).filter(
        ApprovalRequest.request_type == "access_request",
        ApprovalRequest.status.in_(["submitted", "pending"]),
    )

    if current_user.role != "Super Admin":
        query = query.filter(
            ApprovalRequest.company_id == current_user.company_id,
            ApprovalRequest.assigned_approver_id == current_user.id,
        )

    return query.order_by(
        ApprovalRequest.created_at.asc()
    ).all()


@router.post("/{request_id}/review")
def review_access_request(
    request_id: int,
    payload: AccessRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("data_governance", "manage_access")
    ),
):
    ensure_company_access(current_user)

    if current_user.role not in {"Super Admin", "Company Admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot review access requests.",
        )

    decision = payload.decision.strip().lower()

    if decision not in {"approve", "reject"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be approve or reject.",
        )

    query = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == request_id,
        ApprovalRequest.request_type == "access_request",
    )

    if current_user.role != "Super Admin":
        query = query.filter(
            ApprovalRequest.company_id == current_user.company_id,
            ApprovalRequest.assigned_approver_id == current_user.id,
        )

    request = query.with_for_update().first()

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found.",
        )

    if request.status not in {"submitted", "pending"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This request has already been reviewed or is not pending.",
        )

    if request.requested_by == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot approve or reject your own request.",
        )

    changes = request.requested_changes or {}
    permission_id = changes.get("permission_id")
    requested_role = changes.get("role")

    if not permission_id or not requested_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The access request does not contain valid permission details.",
        )

    if requested_role == "Super Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin permissions cannot be granted through this workflow.",
        )

    permission = (
        db.query(Permission)
        .filter(
            Permission.id == permission_id,
            Permission.is_active.is_(True),
        )
        .first()
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The requested permission is no longer active.",
        )

    previous_status = request.status
    now = datetime.now(timezone.utc)

    try:
        if decision == "approve":
            assignment = (
                db.query(RolePermission)
                .filter(
                    RolePermission.company_id == request.company_id,
                    RolePermission.role == requested_role,
                    RolePermission.permission_id == permission.id,
                )
                .first()
            )

            if assignment is None:
                db.add(
                    RolePermission(
                        company_id=request.company_id,
                        role=requested_role,
                        permission_id=permission.id,
                    )
                )

            request.status = "approved"
            action = "APPROVED"
        else:
            request.status = "rejected"
            action = "REJECTED"

        request.assigned_approver_id = current_user.id
        request.updated_at = now
        request.completed_at = now

        db.add(
            ApprovalHistory(
                approval_request_id=request.id,
                company_id=request.company_id,
                user_id=current_user.id,
                action=action,
                from_status=previous_status,
                to_status=request.status,
                comments=payload.comments,
                action_metadata={
                    "permission_id": permission.id,
                    "permission_code": permission.code,
                    "role": requested_role,
                },
            )
        )

        db.add(
            AuditLog(
                company_id=request.company_id,
                user_id=current_user.id,
                module="Data Governance",
                action=(
                    "ACCESS_REQUEST_APPROVED"
                    if decision == "approve"
                    else "ACCESS_REQUEST_REJECTED"
                ),
                resource_type="ApprovalRequest",
                resource_id=request.id,
                description=(
                    f"Access request "
                    f"{'approved' if decision == 'approve' else 'rejected'} "
                    f"for {permission.code}"
                ),
                before_values={"status": previous_status},
                after_values={
                    "status": request.status,
                    "permission_id": permission.id,
                    "role": requested_role,
                },
                status="SUCCESS",
            )
        )

        db.commit()

        return {
            "message": (
                "Access request approved successfully."
                if decision == "approve"
                else "Access request rejected successfully."
            ),
            "request_id": request.id,
            "status": request.status,
            "permission_code": permission.code,
        }

    except Exception:
        db.rollback()
        logger.exception(
            "Failed to review access request %s",
            request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to review access request.",
        )


@router.get("/{request_id}/history")
def get_access_request_history(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_company_access(current_user)

    query = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == request_id,
        ApprovalRequest.request_type == "access_request",
    )

    if current_user.role != "Super Admin":
        query = query.filter(
            ApprovalRequest.company_id == current_user.company_id,
        )

    request = query.first()

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found.",
        )

    if (
        request.requested_by != current_user.id
        and request.assigned_approver_id != current_user.id
        and current_user.role != "Super Admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot view this request history.",
        )

    history = (
        db.query(ApprovalHistory)
        .filter(
            ApprovalHistory.approval_request_id == request.id,
            ApprovalHistory.company_id == request.company_id,
        )
        .order_by(ApprovalHistory.created_at.asc())
        .all()
    )

    return [
        {
            "id": item.id,
            "action": item.action,
            "from_status": item.from_status,
            "to_status": item.to_status,
            "comments": item.comments,
            "user_id": item.user_id,
            "created_at": item.created_at,
        }
        for item in history
    ]