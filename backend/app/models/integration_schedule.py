from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Time,
    CheckConstraint,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class IntegrationSchedule(Base):
    __tablename__ = "integration_schedules"

    id = Column(Integer, primary_key=True, index=True)

    integration_id = Column(
        Integer,
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    frequency = Column(
        String(30),
        nullable=False,
        default="daily"
    )

    day_of_week = Column(Integer, nullable=True)

    scheduled_time = Column(
        Time,
        nullable=True
    )

    timezone = Column(
        String(100),
        nullable=False,
        default="Asia/Kolkata"
    )

    cron_expression = Column(
        String(100),
        nullable=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    next_run_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    last_run_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    last_run_status = Column(
        String(30),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    integration = relationship(
        "Integration",
        back_populates="schedule"
    )

    __table_args__ = (
        CheckConstraint(
            "frequency IN ('daily', 'weekly', 'custom')",
            name="ck_integration_schedule_frequency"
        ),
        CheckConstraint(
            "day_of_week IS NULL OR (day_of_week >= 0 AND day_of_week <= 6)",
            name="ck_integration_schedule_day"
        ),
        Index(
            "ix_integration_schedules_next_run",
            "next_run_at"
        ),
    )