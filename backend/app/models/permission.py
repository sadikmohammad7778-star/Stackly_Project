from sqlalchemy import Column, Integer, String, Text, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.config.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    module = Column(
        String(100),
        nullable=False,
        index=True,
    )

    action = Column(
        String(50),
        nullable=False,
    )

    code = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "module",
            "action",
            name="uq_permissions_module_action",
        ),
    )