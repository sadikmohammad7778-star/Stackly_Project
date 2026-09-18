from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.config.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    module = Column(
        String(100),
        nullable=False,
        index=True,
    )

    action = Column(
        String(100),
        nullable=False,
        index=True,
    )

    resource_type = Column(
        String(100),
        nullable=True,
        index=True,
    )

    resource_id = Column(
        String(100),
        nullable=True,
    )

    description = Column(
        String(255),
        nullable=False,
    )

    before_values = Column(
        JSONB,
        nullable=True,
    )

    after_values = Column(
        JSONB,
        nullable=True,
    )

    ip_address = Column(
        String(50),
        nullable=True,
    )

    browser = Column(
        String(255),
        nullable=True,
    )

    user_agent = Column(
        String(500),
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="SUCCESS",
        server_default="SUCCESS",
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index(
            "ix_audit_logs_company_created_at",
            "company_id",
            "created_at",
        ),
        Index(
            "ix_audit_logs_company_action",
            "company_id",
            "action",
        ),
        Index(
            "ix_audit_logs_company_module",
            "company_id",
            "module",
        ),
    )