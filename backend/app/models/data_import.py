from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.config.database import Base


class DataImport(Base):
    __tablename__ = "data_imports"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    data_type = Column(
        String(30),
        nullable=False,
        index=True
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    status = Column(
        String(30),
        default="Uploaded",
        nullable=False,
        index=True
    )

    total_rows = Column(
        Integer,
        default=0,
        nullable=False
    )

    valid_rows = Column(
        Integer,
        default=0,
        nullable=False
    )

    invalid_rows = Column(
        Integer,
        default=0,
        nullable=False
    )

    duplicate_rows = Column(
        Integer,
        default=0,
        nullable=False
    )

    successful_rows = Column(
        Integer,
        default=0,
        nullable=False
    )

    failed_rows = Column(
        Integer,
        default=0,
        nullable=False
    )

    skipped_rows = Column(
        Integer,
        default=0,
        nullable=False
    )

    processed_rows = Column(
        Integer,
        default=0,
        nullable=False
    )

    progress = Column(
        Integer,
        default=0,
        nullable=False
    )

    error_message = Column(
        Text,
        nullable=True
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    company = relationship("Company")

    user = relationship("User")