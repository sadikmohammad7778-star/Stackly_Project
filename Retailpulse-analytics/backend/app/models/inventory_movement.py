from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.config.database import Base


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)

    inventory_id = Column(
        Integer,
        ForeignKey("inventory.id"),
        nullable=False
    )

    movement_type = Column(String(50), nullable=False)

    quantity_changed = Column(Integer, nullable=False)

    previous_quantity = Column(Integer, nullable=False)

    updated_quantity = Column(Integer, nullable=False)

    reason = Column(String(255), nullable=False)

    remarks = Column(String(500))

    performed_by = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    inventory = relationship(
        "Inventory",
        back_populates="movements"
    )