from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    Index,
)

from app.config.database import Base


class BackgroundJob(Base):
    __tablename__ = "background_jobs"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=True,
        index=True,
    )

    triggered_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    job_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    status = Column(
        String(30),
        default="Pending",
        nullable=False,
        index=True,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    duration_ms = Column(
        Integer,
        nullable=True,
    )

    retry_count = Column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_background_jobs_company_status",
            "company_id",
            "status",
        ),
    )