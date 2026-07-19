from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# -----------------------------
# Sale Item Schemas
# -----------------------------
class SaleItemCreate(BaseModel):
    product_id: int
    category_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount: float = 0
    tax: float = 0


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    category_id: int
    quantity: int
    unit_price: float
    discount: float
    tax: float
    total: float

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Sale Schemas
# -----------------------------
class SaleCreate(BaseModel):
    company_id: int
    customer_name: str
    sales_channel: str
    payment_method: str
    items: List[SaleItemCreate]


class SaleUpdate(BaseModel):
    customer_name: Optional[str] = None
    sales_channel: Optional[str] = None
    payment_method: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    company_id: int
    invoice_number: str
    customer_name: str
    sale_date: datetime
    sales_channel: str
    payment_method: str
    total_amount: float

    items: List[SaleItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Dashboard Summary
# -----------------------------
class SalesSummary(BaseModel):
    total_sales: int
    total_revenue: float
    average_order_value: float