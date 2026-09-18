from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.config.database import Base


class SaleItem(Base):

    __tablename__ = "sale_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sale_id = Column(
        Integer,
        ForeignKey(
            "sales.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    unit_price = Column(
        Float,
        nullable=False
    )

    discount = Column(
        Float,
        default=0,
        nullable=False
    )

    tax = Column(
        Float,
        default=0,
        nullable=False
    )

    total = Column(
        Float,
        nullable=False
    )

    # ========================================================
    # Relationships
    # ========================================================

    sale = relationship(
        "Sale",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )

    category = relationship(
        "Category"
    )

    # ========================================================
    # Response Properties
    # ========================================================

    @property
    def product_name(self):
        if self.product:
            return self.product.name

        return ""

    @property
    def sku(self):
        if self.product:
            return self.product.sku

        return ""