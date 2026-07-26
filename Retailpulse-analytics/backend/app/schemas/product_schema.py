from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    company_id: int
    category_id: int
    name: str
    sku: str
    description: Optional[str] = None
    brand: str
    unit_price: float
    stock_quantity: int
    status: str = "In Stock"
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None

    brand: Optional[str] = None

    unit_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)