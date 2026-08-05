from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ----------------------------
# Create Customer
# ----------------------------

class CustomerCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    customer_type: str
    preferred_sales_channel: Optional[str] = None


# ----------------------------
# Update Customer
# ----------------------------

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    customer_type: Optional[str] = None
    preferred_sales_channel: Optional[str] = None
    status: Optional[str] = None


# ----------------------------
# Purchase Summary
# ----------------------------

class CustomerPurchaseSummaryResponse(BaseModel):
    total_orders: int
    total_revenue: float
    total_products_purchased: int
    average_order_value: float
    purchase_frequency: float
    segment: str

    first_purchase_date: Optional[date]
    last_purchase_date: Optional[date]

    favorite_product_id: Optional[int]
    favorite_category_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Customer Response
# ----------------------------

class CustomerResponse(BaseModel):
    id: int
    company_id: int
    customer_id: str

    full_name: str
    email: EmailStr
    phone: str

    gender: Optional[str]
    date_of_birth: Optional[date]

    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]

    customer_type: str
    preferred_sales_channel: Optional[str]

    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Customer Profile
# ----------------------------

class CustomerProfileResponse(CustomerResponse):
    purchase_summary: Optional[CustomerPurchaseSummaryResponse] = None

    model_config = ConfigDict(from_attributes=True)