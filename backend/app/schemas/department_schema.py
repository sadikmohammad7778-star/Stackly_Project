from pydantic import BaseModel
from typing import Optional


class DepartmentCreate(BaseModel):
    company_id: int
    department_name: str
    description: Optional[str] = None


class DepartmentUpdate(BaseModel):
    company_id: Optional[int] = None
    department_name: Optional[str] = None
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: int
    company_id: int
    department_name: str
    description: Optional[str] = None

    model_config = {
        "from_attributes": True
    }