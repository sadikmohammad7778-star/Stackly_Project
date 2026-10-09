from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Workflow Configuration Base

class WorkflowConfigurationBase(BaseModel):
    request_type: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    approver_role: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    approval_required: bool = True

    allow_self_approval: bool = False

    is_active: bool = True

# Create Workflow Configuration

class WorkflowConfigurationCreate(WorkflowConfigurationBase):
    company_id: int = Field(
        ...,
        gt=0
    )

# Update Workflow Configuration

class WorkflowConfigurationUpdate(BaseModel):
    approver_role: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50
    )

    approval_required: Optional[bool] = None

    allow_self_approval: Optional[bool] = None

    is_active: Optional[bool] = None


# Workflow Configuration Response

class WorkflowConfigurationResponse(WorkflowConfigurationBase):
    id: int

    company_id: int

    created_by: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )