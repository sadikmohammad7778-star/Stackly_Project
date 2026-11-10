from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    CheckConstraint,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class IntegrationSync(Base):
    __tablename__ = "integration_syncs"

    id = Column(Integer, primary_key=True, index=True)

    integration_id = Column(
        Integer,
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    triggered_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    trigger_type = Column(
        String(30),
        nullable=False,
        default="manual"
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending"
    )

    total_records = Column(Integer, nullable=False, default=0)

    processed_records = Column(Integer, nullable=False, default=0)

    inserted_records = Column(Integer, nullable=False, default=0)

    updated_records = Column(Integer, nullable=False, default=0)

    skipped_records = Column(Integer, nullable=False, default=0)

    failed_records = Column(Integer, nullable=False, default=0)

    started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    duration_ms = Column(Integer, nullable=True)

    error_summary = Column(Text, nullable=True)

    execution_metadata = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    integration = relationship(
        "Integration",
        back_populates="syncs"
    )

    company = relationship("Company")

    user = relationship("User")

    errors = relationship(
        "IntegrationSyncError",
        back_populates="sync",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', "
            "'completed_with_errors', 'failed', 'cancelled')",
            name="ck_integration_sync_status"
        ),
        CheckConstraint(
            "trigger_type IN ('manual', 'scheduled', 'retry', 'initial', 'incremental')",
            name="ck_integration_sync_trigger_type"
        ),
        Index(
            "ix_integration_syncs_company_status",
            "company_id",
            "status"
        ),
        Index(
            "ix_integration_syncs_integration_created",
            "integration_id",
            "created_at"
        ),
    )