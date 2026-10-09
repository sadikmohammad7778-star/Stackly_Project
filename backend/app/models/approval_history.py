from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class ApprovalHistory(Base):
    __tablename__ = "approval_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    approval_request_id = Column(
        Integer,
        ForeignKey("approval_requests.id"),
        nullable=False,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    action = Column(
        String(50),
        nullable=False
    )

    from_status = Column(
        String(30),
        nullable=True
    )

    to_status = Column(
        String(30),
        nullable=True
    )

    comments = Column(
        Text,
        nullable=True
    )

    action_metadata = Column(
        "metadata",
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Request
    approval_request = relationship(
        "ApprovalRequest",
        back_populates="history"
    )

    # Company
    company = relationship(
        "Company",
        back_populates="approval_histories"
    )

    user = relationship(
        "User",
        back_populates="approval_history"
    )