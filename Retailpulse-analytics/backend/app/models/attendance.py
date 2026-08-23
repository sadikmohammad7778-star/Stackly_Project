from sqlalchemy import (
    Column,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
    )

    attendance_date = Column(
        Date,
        nullable=False,
    )

    check_in = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    check_out = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    status = Column(
        String(20),
        default="Present",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    employee = relationship(
        "Employee",
        back_populates="attendance_records",
    )