from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    company_id: int
    category_id: int

    name: str
    sku: str
    brand: str

    description: Optional[str] = None

    unit_price: float = Field(gt=0)
    cost_price: float

    stock_quantity: int = Field(ge=0)

    unit_of_measure: str

    status: str = "Active"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    cost_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    unit_of_measure: Optional[str] = None
    status: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True