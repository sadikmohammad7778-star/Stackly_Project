from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    company_id: int
    name: str
    description: Optional[str] = None
    status: str = "Active"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True