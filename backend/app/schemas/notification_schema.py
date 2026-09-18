from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int

    company_id: int
    user_id: int

    type: str
    title: str
    message: str
    priority: str

    resource_type: Optional[str] = None
    resource_id: Optional[int] = None

    is_read: bool

    created_at: datetime
    read_at: Optional[datetime] = None

    expires_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]

    total: int
    page: int
    page_size: int

    unread_count: int