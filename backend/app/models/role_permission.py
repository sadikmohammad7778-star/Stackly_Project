from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Index,
)

from app.config.database import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(
        String(30),
        nullable=False,
        index=True,
    )

    permission_id = Column(
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "role",
            "permission_id",
            name="uq_company_role_permission",
        ),
        Index(
            "ix_role_permissions_company_role",
            "company_id",
            "role",
        ),
    )