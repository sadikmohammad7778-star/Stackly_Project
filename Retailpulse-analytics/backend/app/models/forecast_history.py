from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class ForecastHistory(Base):
    __tablename__ = "forecast_history"

    id = Column(Integer, primary_key=True, index=True)

    forecast_id = Column(
        Integer,
        ForeignKey("demand_forecasts.id", ondelete="CASCADE"),
        nullable=False,
    )

    historical_sales = Column(Float, nullable=False)

    prediction = Column(Float, nullable=False)

    accuracy = Column(Float, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    forecast = relationship(
        "DemandForecast",
        back_populates="history",
    )