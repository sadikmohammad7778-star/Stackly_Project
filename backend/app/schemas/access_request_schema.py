from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AccessRequestCreate(BaseModel):
    permission_id: int = Field(gt=0)
    reason: str = Field(min_length=5, max_length=2000)
    priority: str = "medium"


class AccessRequestReview(BaseModel):
    decision: str
    comments: Optional[str] = None


class AccessRequestResponse(BaseModel):
    id: int
    company_id: int
    request_type: str
    requested_by: int
    assigned_approver_id: Optional[int]
    requested_changes: Optional[dict]
    reason: str
    priority: str
    status: str
    created_at: datetime
    submitted_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True