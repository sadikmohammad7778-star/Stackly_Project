from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# -----------------------------
# Inventory
# -----------------------------
class InventoryBase(BaseModel):
    reorder_level: int = Field(..., ge=0)


class InventoryResponse(BaseModel):
    id: int
    company_id: int
    product_id: int

    current_stock: int
    reserved_stock: int
    available_stock: int

    reorder_level: int
    stock_status: str

    updated_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# Add Stock
# -----------------------------
class AddStockRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    reason: str
    remarks: Optional[str] = None


# -----------------------------
# Remove Stock
# -----------------------------
class RemoveStockRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    reason: str
    remarks: Optional[str] = None


# -----------------------------
# Manual Adjustment
# -----------------------------
class AdjustStockRequest(BaseModel):
    product_id: int
    quantity: int
    reason: str
    remarks: Optional[str] = None


# -----------------------------
# Reorder Level
# -----------------------------
class ReorderLevelUpdate(BaseModel):
    reorder_level: int = Field(..., ge=0)


# -----------------------------
# Movement History
# -----------------------------
class InventoryMovementResponse(BaseModel):
    id: int
    inventory_id: int

    movement_type: str

    quantity_changed: int

    previous_quantity: int

    updated_quantity: int

    reason: str

    remarks: Optional[str]

    performed_by: Optional[int]

    created_at: datetime

    class Config:
        from_attributes = True