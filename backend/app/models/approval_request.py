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


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    request_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    requested_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    assigned_approver_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    related_entity_type = Column(
        String(50),
        nullable=True
    )

    related_entity_id = Column(
        Integer,
        nullable=True
    )

    requested_changes = Column(
        JSON,
        nullable=True
    )

    reason = Column(
        Text,
        nullable=False
    )

    priority = Column(
        String(20),
        default="medium",
        nullable=False
    )

    status = Column(
        String(30),
        default="draft",
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Company
    company = relationship(
        "Company",
        back_populates="approval_requests"
    )

    # Requester
    requester = relationship(
        "User",
        foreign_keys=[requested_by],
        back_populates="submitted_approval_requests"
    )

    # Assigned approver
    assigned_approver = relationship(
        "User",
        foreign_keys=[assigned_approver_id],
        back_populates="assigned_approval_requests"
    )

    # Approval history
    history = relationship(
        "ApprovalHistory",
        back_populates="approval_request",
        cascade="all, delete-orphan"
    )