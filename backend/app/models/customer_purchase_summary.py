from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class CustomerPurchaseSummary(Base):
    __tablename__ = "customer_purchase_summary"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    total_orders = Column(Integer, default=0)

    total_revenue = Column(Float, default=0)

    total_products_purchased = Column(Integer, default=0)

    average_order_value = Column(Float, default=0)

    purchase_frequency = Column(Float, default=0)

    first_purchase_date = Column(Date)

    last_purchase_date = Column(Date)

    favorite_product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=True,
    )

    favorite_category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
    )

    # Customer Segment
    segment = Column(
        String(50),
        default="New Customer",
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships

    customer = relationship(
        "Customer",
        back_populates="purchase_summary",
    )

    favorite_product = relationship(
        "Product",
        back_populates="customer_purchase_summaries",
    )

    favorite_category = relationship(
        "Category",
        back_populates="customer_purchase_summaries",
    )