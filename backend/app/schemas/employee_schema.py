from datetime import date
from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    designation: str
    salary: float
    joining_date: date
    status: bool = True
    department_id: int | None = None


class EmployeeUpdate(BaseModel):
    company_id: int
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    designation: str
    salary: float
    joining_date: date
    status: bool


class EmployeeResponse(BaseModel):
    id: int
    company_id: int
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    designation: str
    salary: float
    joining_date: date
    status: bool

    class Config:
        from_attributes = True