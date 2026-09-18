from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# ------------------------------------
# Sale Item Schemas
# ------------------------------------

class SaleItemCreate(BaseModel):
    product_id: int
    category_id: int

    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity must be greater than zero"
    )

    unit_price: float = Field(
        ...,
        gt=0,
        description="Unit price must be greater than zero"
    )

    discount: float = Field(
        0,
        ge=0,
        description="Discount cannot be negative"
    )

    tax: float = Field(
        0,
        ge=0,
        description="Tax cannot be negative"
    )


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


# ------------------------------------
# Sale Schemas
# ------------------------------------

class SaleCreate(BaseModel):
    company_id: int
    customer_id: int

    sales_channel: str = Field(
        ...,
        min_length=1
    )

    payment_method: str = Field(
        ...,
        min_length=1
    )

    discount: float = Field(
        0,
        ge=0
    )

    tax: float = Field(
        0,
        ge=0
    )

    items: List[SaleItemCreate] = Field(
        ...,
        min_length=1
    )


class SaleUpdate(BaseModel):
    customer_id: Optional[int] = None

    sales_channel: Optional[str] = None

    payment_method: Optional[str] = None

    discount: Optional[float] = Field(
        None,
        ge=0
    )

    tax: Optional[float] = Field(
        None,
        ge=0
    )

    status: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    company_id: int

    invoice_number: str

    customer_id: int
    customer_name: str

    sale_date: datetime

    sales_channel: str
    payment_method: str

    discount: float
    tax: float

    total_amount: float

    status: str

    items: List[SaleItemDetailResponse] = []
# ------------------------------------
# Dashboard Summary
# ------------------------------------

class SalesSummary(BaseModel):
    total_sales: int
    total_revenue: float
    average_order_value: float


class SaleItemDetailResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    sku: str
    category_id: int
    quantity: int
    unit_price: float
    discount: float
    tax: float
    total: float