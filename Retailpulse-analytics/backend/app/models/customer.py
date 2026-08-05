from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    customer_id = Column(String(20), unique=True, nullable=False)

    full_name = Column(String(150), nullable=False)

    email = Column(String(150), nullable=False)

    phone = Column(String(20), nullable=False)

    gender = Column(String(20))

    date_of_birth = Column(Date)

    address = Column(String(255))

    city = Column(String(100))

    state = Column(String(100))

    country = Column(String(100))

    customer_type = Column(String(50), nullable=False)

    preferred_sales_channel = Column(String(50))

    status = Column(String(20), default="Active")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships

    company = relationship(
        "Company",
        back_populates="customers",
    )

    purchase_summary = relationship(
        "CustomerPurchaseSummary",
        back_populates="customer",
        uselist=False,
        cascade="all, delete",
    )


    timeline = relationship(
        "CustomerTimeline",
        back_populates="customer",
        cascade="all, delete",
    )