from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.config.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)

    users = relationship(
        "User",
        back_populates="company",
        cascade="all, delete"
    )

    employees = relationship(
    "Employee",
    back_populates="company",
    cascade="all, delete",
    )
    departments = relationship(
    "Department",
    back_populates="company",
    cascade="all, delete"
    )

    inventories = relationship(
    "Inventory",
    back_populates="company",
    cascade="all, delete"
)
