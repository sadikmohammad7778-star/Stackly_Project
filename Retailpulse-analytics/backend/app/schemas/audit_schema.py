from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int

    company_id: int
    user_id: int

    module: str
    action: str

    resource_type: str | None = None
    resource_id: str | None = None

    description: str

    before_values: dict[str, Any] | None = None
    after_values: dict[str, Any] | None = None

    ip_address: str | None = None
    browser: str | None = None
    user_agent: str | None = None

    status: str

    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]

    total: int
    page: int
    limit: int
    total_pages: int

    total_creates: int
    total_updates: int
    total_deletes: int