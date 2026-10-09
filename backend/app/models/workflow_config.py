from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class WorkflowConfiguration(Base):
    __tablename__ = "workflow_configurations"

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

    approver_role = Column(
        String(50),
        nullable=False
    )

    approval_required = Column(
        Boolean,
        default=True,
        nullable=False
    )

    allow_self_approval = Column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Company
    company = relationship(
        "Company",
        back_populates="workflow_configurations"
    )

    # Admin/user who created configuration
    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_workflow_configurations"
    )