from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.approval_request import ApprovalRequest
from app.models.approval_history import ApprovalHistory
from app.models.workflow_config import WorkflowConfiguration
from app.models.user import User


VALID_REQUEST_TYPES = {
    "stock_adjustment",
    "product_deactivation",
    "product_price_change",
    "customer_information_change",
    "inventory_import",
}

VALID_STATUSES = {
    "draft",
    "submitted",
    "pending_approval",
    "approved",
    "rejected",
    "cancelled",
}

VALID_PRIORITIES = {
    "low",
    "medium",
    "high",
    "critical",
}


def create_approval_request(
    db: Session,
    request_data,
    current_user: User,
):
    if request_data.request_type not in VALID_REQUEST_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid request type."
        )

    if request_data.priority not in VALID_PRIORITIES:
        raise HTTPException(
            status_code=400,
            detail="Invalid priority."
        )

    if request_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot create a request for another company."
        )

    workflow_config = (
        db.query(WorkflowConfiguration)
        .filter(
            WorkflowConfiguration.company_id == current_user.company_id,
            WorkflowConfiguration.request_type == request_data.request_type,
            WorkflowConfiguration.is_active == True,
        )
        .first()
    )

    if not workflow_config:
        raise HTTPException(
            status_code=400,
            detail="No active workflow configuration found for this request type."
        )

    approver = None

    if workflow_config.approval_required:
        approver = (
            db.query(User)
            .filter(
                User.company_id == current_user.company_id,
                User.role == workflow_config.approver_role,
                User.status == True,
            )
            .first()
        )

        if not approver:
            raise HTTPException(
                status_code=400,
                detail="No eligible approver found."
            )

    approval_request = ApprovalRequest(
        company_id=current_user.company_id,
        request_type=request_data.request_type,
        requested_by=current_user.id,
        assigned_approver_id=approver.id if approver else None,
        related_entity_type=request_data.related_entity_type,
        related_entity_id=request_data.related_entity_id,
        requested_changes=request_data.requested_changes,
        reason=request_data.reason,
        priority=request_data.priority,
        status="draft",
        submitted_at=None,
    )

    db.add(approval_request)
    db.flush()

    history = ApprovalHistory(
        approval_request_id=approval_request.id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="REQUEST_CREATED",
        from_status=None,
        to_status="draft",
        comments=None,
        action_metadata={
            "request_type": request_data.request_type,
            "approver_id": approver.id if approver else None,
            "approval_required": workflow_config.approval_required,
        },
    )

    db.add(history)
    db.commit()
    db.refresh(approval_request)

    return approval_request

def get_approval_request(
    db: Session,
    request_id: int,
    current_user: User,
):
    approval_request = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.id == request_id,
            ApprovalRequest.company_id == current_user.company_id,
        )
        .first()
    )

    if not approval_request:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found."
        )

    return approval_request


def get_approval_requests(
    db: Session,
    current_user: User,
    status_filter=None,
    request_type=None,
    search=None,
    page=1,
    page_size=10,
):
    query = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.company_id == current_user.company_id
        )
    )

    if status_filter:
        query = query.filter(
            ApprovalRequest.status == status_filter
        )

    if request_type:
        query = query.filter(
            ApprovalRequest.request_type == request_type
        )

    if search:
        if search.isdigit():
            query = query.filter(
                ApprovalRequest.id == int(search)
            )

    total = query.count()

    requests = (
        query
        .order_by(ApprovalRequest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": requests,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


def get_my_requests(
    db: Session,
    current_user: User,
    page=1,
    page_size=10,
):
    query = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.company_id == current_user.company_id,
            ApprovalRequest.requested_by == current_user.id,
        )
    )

    total = query.count()

    requests = (
        query
        .order_by(ApprovalRequest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": requests,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


def get_pending_requests(
    db: Session,
    current_user: User,
    page=1,
    page_size=10,
):
    query = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.company_id == current_user.company_id,
            ApprovalRequest.status == "pending_approval",
            ApprovalRequest.assigned_approver_id == current_user.id,
        )
    )

    total = query.count()

    requests = (
        query
        .order_by(ApprovalRequest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": requests,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


def get_approval_history(
    db: Session,
    request_id: int,
    current_user: User,
):
    approval_request = get_approval_request(
        db,
        request_id,
        current_user,
    )

    return (
        db.query(ApprovalHistory)
        .filter(
            ApprovalHistory.approval_request_id == approval_request.id,
            ApprovalHistory.company_id == current_user.company_id,
        )
        .order_by(ApprovalHistory.created_at.asc())
        .all()
    )


def cancel_approval_request(
    db: Session,
    request_id: int,
    current_user: User,
    comments=None,
):
    approval_request = get_approval_request(
        db,
        request_id,
        current_user,
    )

    if approval_request.requested_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only cancel your own requests."
        )

    if approval_request.status not in {
        "draft",
        "submitted",
        "pending_approval",
    }:
        raise HTTPException(
            status_code=400,
            detail="This request cannot be cancelled."
        )

    previous_status = approval_request.status

    approval_request.status = "cancelled"
    approval_request.completed_at = datetime.now(timezone.utc)

    history = ApprovalHistory(
        approval_request_id=approval_request.id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="REQUEST_CANCELLED",
        from_status=previous_status,
        to_status="cancelled",
        comments=comments,
        action_metadata={
            "request_type": approval_request.request_type,
            "related_entity_type": approval_request.related_entity_type,
            "related_entity_id": approval_request.related_entity_id,
        },
    )

    db.add(history)
    db.commit()
    db.refresh(approval_request)

    return approval_request


def reject_approval_request(
    db: Session,
    request_id: int,
    current_user: User,
    comments: str,
):
    approval_request = get_approval_request(
        db,
        request_id,
        current_user,
    )

    if approval_request.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="Only pending requests can be rejected."
        )

    if approval_request.assigned_approver_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to reject this request."
        )

    if approval_request.requested_by == current_user.id:
        config = (
            db.query(WorkflowConfiguration)
            .filter(
                WorkflowConfiguration.company_id == current_user.company_id,
                WorkflowConfiguration.request_type == approval_request.request_type,
                WorkflowConfiguration.is_active == True,
            )
            .first()
        )

        if not config or not config.allow_self_approval:
            raise HTTPException(
                status_code=403,
                detail="You cannot reject your own request."
            )

    if not comments or not comments.strip():
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required."
        )

    approval_request.status = "rejected"
    approval_request.completed_at = datetime.now(timezone.utc)

    history = ApprovalHistory(
        approval_request_id=approval_request.id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="REQUEST_REJECTED",
        from_status="pending_approval",
        to_status="rejected",
        comments=comments.strip(),
        action_metadata={
            "request_type": approval_request.request_type,
            "related_entity_type": approval_request.related_entity_type,
            "related_entity_id": approval_request.related_entity_id,
        },
    )

    db.add(history)
    db.commit()
    db.refresh(approval_request)

    return approval_request


def get_pending_count(
    db: Session,
    current_user: User,
):
    return (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.company_id == current_user.company_id,
            ApprovalRequest.status == "pending_approval",
            ApprovalRequest.assigned_approver_id == current_user.id,
        )
        .count()
    )