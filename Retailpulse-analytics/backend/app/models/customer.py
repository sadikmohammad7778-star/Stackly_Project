from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    customer_id = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    # ------------------------------------
    # Customer Information
    # ------------------------------------

    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    phone = Column(
        String(20),
        unique=True,
        nullable=False,
    )

    # ------------------------------------
    # Address
    # ------------------------------------

    address = Column(
        String(255),
        nullable=False,
    )

    city = Column(
        String(100),
        nullable=False,
    )

    state = Column(
        String(100),
        nullable=False,
    )

    country = Column(
        String(100),
        nullable=False,
    )

    postal_code = Column(
        String(20),
        nullable=False,
    )

    # ------------------------------------
    # Customer Details
    # ------------------------------------

    segment = Column(
        String(20),
        default="New",
        nullable=False,
    )

    status = Column(
        String(20),
        default="Active",
        nullable=False,
    )

    # ------------------------------------
    # Purchase Information
    # ------------------------------------

    total_orders = Column(
        Integer,
        default=0,
        nullable=False,
    )

    total_spend = Column(
        Float,
        default=0.0,
        nullable=False,
    )

    last_purchase_date = Column(
        DateTime,
        nullable=True,
    )

    # ------------------------------------
    # Audit Fields
    # ------------------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------
    # Relationships
    # ------------------------------------

    company = relationship(
        "Company",
        back_populates="customers",
    )

    sales = relationship(
        "Sale",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    purchase_summary = relationship(
        "CustomerPurchaseSummary",
        back_populates="customer",
        uselist=False,
        cascade="all, delete-orphan",
    )

    timeline = relationship(
        "CustomerTimeline",
        back_populates="customer",
        cascade="all, delete-orphan",
    )