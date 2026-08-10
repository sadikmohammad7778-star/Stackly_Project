from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# =========================================
# Base Customer Schema
# =========================================

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

    address: str
    city: str
    state: str
    country: str
    postal_code: str

    segment: str = "New"
    status: str = "Active"


# =========================================
# Create Customer
# =========================================

class CustomerCreate(CustomerBase):
    pass


# =========================================
# Update Customer
# =========================================

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    segment: Optional[str] = None
    status: Optional[str] = None


# =========================================
# Purchase Summary
# =========================================

class PurchaseSummary(BaseModel):
    total_orders: int = 0
    total_revenue: float = 0
    average_order_value: float = 0
    total_products_purchased: int = 0
    purchase_frequency: float = 0

    first_purchase_date: Optional[datetime] = None
    last_purchase_date: Optional[datetime] = None


# =========================================
# Customer Response
# =========================================

class CustomerResponse(CustomerBase):
    id: int
    company_id: int
    customer_id: str

    total_orders: int = 0
    total_spend: float = 0
    last_purchase_date: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================
# Customer Profile Response
# =========================================

class CustomerProfileResponse(CustomerResponse):
    purchase_summary: PurchaseSummary = PurchaseSummary()

    model_config = ConfigDict(from_attributes=True)