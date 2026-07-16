from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.config.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(Integer, nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    name = Column(String(150), nullable=False)

    sku = Column(String(50), nullable=False)

    brand = Column(String(100))

    description = Column(String(500))

    unit_price = Column(Float, nullable=False)

    cost_price = Column(Float, nullable=False)

    stock_quantity = Column(Integer, default=0)

    unit_of_measure = Column(String(50))

    status = Column(String(20), default="Active")

    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )