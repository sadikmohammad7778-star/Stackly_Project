from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
    )

    employee_code = Column(
        String(30),
        unique=True,
        nullable=False,
    )

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
    )

    phone = Column(
        String(20),
        nullable=False,
    )

    designation = Column(
        String(100),
        nullable=False,
    )

    salary = Column(
        Float,
        nullable=False,
    )

    joining_date = Column(
        Date,
        nullable=False,
    )

    status = Column(
        Boolean,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=True
    )

    company = relationship(
        "Company",
        back_populates="employees",
    )

    attendance_records = relationship(
            
        "Attendance",
        back_populates="employee",
        cascade="all, delete",

        )
    
    department = relationship(
        "Department",
        back_populates="employees"
)