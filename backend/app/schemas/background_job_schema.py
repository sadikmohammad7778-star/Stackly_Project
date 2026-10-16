from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BackgroundJobResponse(BaseModel):
    id: int
    company_id: Optional[int] = None
    triggered_by: Optional[int] = None
    job_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    retry_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)