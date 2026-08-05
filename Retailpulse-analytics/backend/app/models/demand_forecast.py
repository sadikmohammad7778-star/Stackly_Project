from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    forecast_period = Column(String(50), nullable=False)

    predicted_demand = Column(Float, nullable=False)

    confidence_score = Column(Float, default=0)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company")
    product = relationship("Product")
    category = relationship("Category")

    history = relationship(
        "ForecastHistory",
        back_populates="forecast",
        cascade="all, delete",
    )

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "product_id",
            "forecast_period",
            name="uq_product_forecast_period",
        ),
    )