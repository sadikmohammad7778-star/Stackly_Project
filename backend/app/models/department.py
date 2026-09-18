from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.config.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    department_name = Column(
        String(100),
        nullable=False
    )

    description = Column(
        String(255)
    )

    company = relationship(
        "Company",
        back_populates="departments"
    )

    employees = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete"
    )