from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    employee_id: int
    attendance_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str = "Present"


class AttendanceUpdate(BaseModel):
    attendance_date: Optional[date] = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    attendance_date: date
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    status: str

    model_config = {
        "from_attributes": True
    }