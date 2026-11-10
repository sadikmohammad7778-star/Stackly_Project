from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    JSON,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class IntegrationMapping(Base):
    __tablename__ = "integration_mappings"

    id = Column(Integer, primary_key=True, index=True)

    integration_id = Column(
        Integer,
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False
    )

    source_field = Column(String(150), nullable=False)

    target_field = Column(String(150), nullable=False)

    source_type = Column(String(50), nullable=True)

    target_type = Column(String(50), nullable=False)

    is_required = Column(Boolean, default=False, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    transformation_config = Column(JSON, nullable=True)

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
        back_populates="mappings"
    )

    __table_args__ = (
        UniqueConstraint(
            "integration_id",
            "source_field",
            name="uq_integration_source_field"
        ),
        Index(
            "ix_integration_mappings_integration",
            "integration_id"
        ),
    )