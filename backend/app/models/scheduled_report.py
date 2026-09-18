from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.config.database import Base


class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    report_type = Column(
        String(50),
        nullable=False,
    )

    filters = Column(
        Text,
        nullable=True,
    )

    frequency = Column(
        String(20),
        nullable=False,
    )

    execution_time = Column(
        String(10),
        nullable=False,
    )

    recipients = Column(
        Text,
        nullable=False,
    )

    format = Column(
        String(20),
        nullable=False,
        default="PDF",
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    last_generated_at = Column(
        DateTime,
        nullable=True,
    )

    last_status = Column(
        String(30),
        nullable=True,
    )

    last_error = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    company = relationship("Company")

    user = relationship("User")