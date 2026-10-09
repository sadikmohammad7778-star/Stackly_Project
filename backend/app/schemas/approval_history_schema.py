from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Approval History Response

class ApprovalHistoryResponse(BaseModel):
    id: int

    approval_request_id: int

    company_id: int

    user_id: Optional[int] = None

    action: str

    from_status: Optional[str] = None

    to_status: Optional[str] = None

    comments: Optional[str] = None

    action_metadata: Optional[Dict[str, Any]] = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )