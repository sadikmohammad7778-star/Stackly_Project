from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.config.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        unique=True,
        nullable=False
    )

    current_stock = Column(
        Integer,
        default=0,
        nullable=False
    )

    reserved_stock = Column(
        Integer,
        default=0,
        nullable=False
    )

    available_stock = Column(
        Integer,
        default=0,
        nullable=False
    )

    reorder_level = Column(
        Integer,
        default=10,
        nullable=False
    )

    stock_status = Column(
        String(50),
        default="In Stock",
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Company relationship
    company = relationship(
        "Company",
        back_populates="inventories"
    )

    # Product relationship
    product = relationship(
        "Product",
        back_populates="inventory"
    )

    # Stock movement relationship
    movements = relationship(
        "InventoryMovement",
        back_populates="inventory",
        cascade="all, delete-orphan"
    )