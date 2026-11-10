from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    JSON,
    Boolean,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class IntegrationSyncError(Base):
    __tablename__ = "integration_sync_errors"

    id = Column(Integer, primary_key=True, index=True)

    sync_id = Column(
        Integer,
        ForeignKey("integration_syncs.id", ondelete="CASCADE"),
        nullable=False
    )

    source_record_id = Column(
        String(150),
        nullable=True
    )

    row_number = Column(
        Integer,
        nullable=True
    )

    error_category = Column(
        String(100),
        nullable=False
    )

    error_message = Column(
        Text,
        nullable=False
    )

    source_data = Column(
        JSON,
        nullable=True
    )

    retry_status = Column(
        String(30),
        nullable=False,
        default="pending"
    )

    retry_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    is_retryable = Column(
        Boolean,
        nullable=False,
        default=True
    )

    last_retry_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    sync = relationship(
        "IntegrationSync",
        back_populates="errors"
    )

    __table_args__ = (
        Index(
            "ix_integration_sync_errors_sync",
            "sync_id"
        ),
        Index(
            "ix_integration_sync_errors_retry",
            "retry_status",
            "is_retryable"
        ),
    )