from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Approval Request Base Schema
# ============================================================

class ApprovalRequestBase(BaseModel):
    request_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type of approval request"
    )

    related_entity_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Related entity type such as inventory, product, customer, import"
    )

    related_entity_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID of the related business record"
    )

    requested_changes: Optional[Dict[str, Any]] = Field(
        None,
        description="Requested changes to the related record"
    )

    reason: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Reason for requesting the change"
    )

    priority: str = Field(
        default="medium",
        description="Request priority"
    )


# Create Approval Request

class ApprovalRequestCreate(ApprovalRequestBase):
    company_id: int = Field(
        ...,
        gt=0
    )


# Submit Approval Request

class ApprovalRequestSubmit(BaseModel):
    comments: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional submission comments"
    )


# Approve Approval Request

class ApprovalRequestApprove(BaseModel):
    comments: Optional[str] = Field(
        None,
        max_length=2000,
        description="Approval comments"
    )


# Reject Approval Request

class ApprovalRequestReject(BaseModel):
    comments: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Reason for rejecting the request"
    )


# Cancel Approval Request

class ApprovalRequestCancel(BaseModel):
    comments: Optional[str] = Field(
        None,
        max_length=2000,
        description="Cancellation reason or comments"
    )

# Approval Request Response

class ApprovalRequestResponse(ApprovalRequestBase):
    id: int

    company_id: int

    requested_by: int

    assigned_approver_id: Optional[int] = None

    status: str

    created_at: datetime

    submitted_at: Optional[datetime] = None

    updated_at: datetime

    completed_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )