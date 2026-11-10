from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    JSON,
    Text,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(String(150), nullable=False)

    source_type = Column(String(30), nullable=False)

    connection_config = Column(JSON, nullable=False, default=dict)

    encrypted_credentials = Column(Text, nullable=True)

    target_module = Column(String(50), nullable=False)

    sync_strategy = Column(
        String(20),
        nullable=False,
        default="insert"
    )

    status = Column(
        String(20),
        nullable=False,
        default="inactive"
    )

    is_enabled = Column(Boolean, nullable=False, default=False)

    last_sync_at = Column(DateTime(timezone=True), nullable=True)

    last_source_sync_at = Column(
        DateTime(timezone=True),
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

    company = relationship(
        "Company",
        back_populates="integrations"
    )

    creator = relationship("User")

    mappings = relationship(
        "IntegrationMapping",
        back_populates="integration",
        cascade="all, delete-orphan"
    )

    schedule = relationship(
        "IntegrationSchedule",
        back_populates="integration",
        uselist=False,
        cascade="all, delete-orphan"
    )

    syncs = relationship(
        "IntegrationSync",
        back_populates="integration",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_integrations_company_status",
            "company_id",
            "status"
        ),
        Index(
            "ix_integrations_company_source",
            "company_id",
            "source_type"
        ),
    )