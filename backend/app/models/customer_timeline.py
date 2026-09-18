from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class CustomerTimeline(Base):
    __tablename__ = "customer_timeline"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )

    event = Column(String(200), nullable=False)

    description = Column(String(500))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    customer = relationship(
        "Customer",
        back_populates="timeline",
    )