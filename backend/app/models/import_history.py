from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.config.database import Base


class ImportHistory(Base):
    __tablename__ = "import_history"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    import_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    filename = Column(
        String(255),
        nullable=False
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    total_records = Column(
        Integer,
        default=0,
        nullable=False
    )

    valid_records = Column(
        Integer,
        default=0,
        nullable=False
    )

    successful_records = Column(
        Integer,
        default=0,
        nullable=False
    )

    failed_records = Column(
        Integer,
        default=0,
        nullable=False
    )

    duplicate_records = Column(
        Integer,
        default=0,
        nullable=False
    )

    skipped_records = Column(
        Integer,
        default=0,
        nullable=False
    )

    processed_records = Column(
        Integer,
        default=0,
        nullable=False
    )

    progress_percentage = Column(
        Integer,
        default=0,
        nullable=False
    )

    status = Column(
        String(50),
        default="Uploaded",
        nullable=False,
        index=True
    )

    created_at = Column(
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

    processing_duration = Column(
        Integer,
        nullable=True
    )

    company = relationship("Company")

    user = relationship("User")

    errors = relationship(
        "ImportError",
        back_populates="import_history",
        cascade="all, delete-orphan"
    )