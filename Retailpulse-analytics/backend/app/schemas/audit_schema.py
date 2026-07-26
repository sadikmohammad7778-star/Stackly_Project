from datetime import datetime
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int

    company_id: int
    user_id: int

    module: str
    action: str
    description: str

    ip_address: str | None = None
    browser: str | None = None

    created_at: datetime

    class Config:
        from_attributes = True