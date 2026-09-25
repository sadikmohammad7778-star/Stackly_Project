from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Company-level isolation
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Issue classification
    issue_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    severity = Column(
        String(20),
        nullable=False,
        default="WARNING",
        index=True
    )

    module = Column(
        String(50),
        nullable=False,
        index=True
    )

    # Record affected by the issue
    affected_record_type = Column(
        String(50),
        nullable=True
    )

    affected_record_id = Column(
        Integer,
        nullable=True
    )

    # Unique identifier used to prevent duplicate unresolved issues
    issue_key = Column(
        String(255),
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=False
    )

    # Additional information about the issue
    details = Column(
        JSON,
        nullable=True
    )

    # OPEN / INVESTIGATING / RESOLVED / IGNORED
    status = Column(
        String(30),
        nullable=False,
        default="OPEN",
        index=True
    )

    detected_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    resolved_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    resolution_note = Column(
        Text,
        nullable=True
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

    # Relationships
    company = relationship(
        "Company",
        back_populates="data_quality_issues"
    )

    resolver = relationship(
        "User",
        foreign_keys=[resolved_by]
    )

    __table_args__ = (
        Index(
            "ix_dq_issue_company_status",
            "company_id",
            "status"
        ),
        Index(
            "ix_dq_issue_company_type",
            "company_id",
            "issue_type"
        ),
        Index(
            "ix_dq_issue_company_module",
            "company_id",
            "module"
        ),
    )


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Company-level isolation
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # User who triggered reconciliation
    triggered_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    records_checked = Column(
        Integer,
        default=0,
        nullable=False
    )

    issues_detected = Column(
        Integer,
        default=0,
        nullable=False
    )

    issues_resolved = Column(
        Integer,
        default=0,
        nullable=False
    )

    failed_checks = Column(
        Integer,
        default=0,
        nullable=False
    )

    # RUNNING / COMPLETED / COMPLETED_WITH_ISSUES / FAILED
    execution_status = Column(
        String(40),
        nullable=False,
        default="RUNNING",
        index=True
    )

    error_message = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    company = relationship(
        "Company",
        back_populates="reconciliation_runs"
    )

    triggered_user = relationship(
        "User",
        foreign_keys=[triggered_by]
    )

    __table_args__ = (
        Index(
            "ix_reconciliation_company_status",
            "company_id",
            "execution_status"
        ),
    )