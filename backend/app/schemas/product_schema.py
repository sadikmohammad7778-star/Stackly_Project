from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Product Base Schema
# ============================================================

class ProductBase(BaseModel):
    company_id: int
    category_id: int

    name: str = Field(
        ...,
        min_length=1,
        max_length=150
    )

    description: Optional[str] = None

    brand: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    unit_price: float = Field(
        ...,
        gt=0,
        description="Unit price must be greater than zero"
    )

    stock_quantity: int = Field(
        ...,
        ge=0,
        description="Stock quantity cannot be negative"
    )

    is_active: bool = True


# ============================================================
# Create Product
# ============================================================

class ProductCreate(ProductBase):
    pass


# ============================================================
# Update Product
# ============================================================

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=150
    )

    description: Optional[str] = None

    brand: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100
    )

    unit_price: Optional[float] = Field(
        None,
        gt=0,
        description="Unit price must be greater than zero"
    )

    stock_quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Stock quantity cannot be negative"
    )

    is_active: Optional[bool] = None


# ============================================================
# Product Response
# ============================================================

class ProductResponse(ProductBase):
    id: int
    sku: str

    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )