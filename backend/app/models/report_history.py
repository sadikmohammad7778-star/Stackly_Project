from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.config.database import Base


class ReportHistory(Base):
    __tablename__ = "report_history"

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

    generated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    report_name = Column(
        String(100),
        nullable=False,
    )

    filters = Column(
        Text,
        nullable=True,
    )

    format = Column(
        String(20),
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="Success",
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    file_path = Column(
        Text,
        nullable=True,
    )

    generated_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    company = relationship("Company")

    user = relationship("User")