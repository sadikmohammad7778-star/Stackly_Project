from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)

from app.config.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(Integer, nullable=False, index=True)

    user_id = Column(Integer, nullable=False, index=True)

    type = Column(String(50), nullable=False, index=True)

    title = Column(String(255), nullable=False)

    message = Column(Text, nullable=False)

    priority = Column(
        String(20),
        nullable=False,
        default="LOW",
        index=True,
    )

    resource_type = Column(String(50), nullable=True)

    resource_id = Column(Integer, nullable=True)

    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")),
        index=True,
    )
    read_at = Column(DateTime, nullable=True)

    expires_at = Column(DateTime, nullable=True)

    resolved_at = Column(DateTime, nullable=True)

    dedupe_key = Column(
        String(255),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index(
            "ix_notifications_company_user",
            "company_id",
            "user_id",
        ),
        Index(
            "ix_notifications_dedupe",
            "company_id",
            "user_id",
            "dedupe_key",
        ),
    )