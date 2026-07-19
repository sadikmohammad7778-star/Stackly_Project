from pydantic import BaseModel


class RevenueReport(BaseModel):
    today: float
    this_week: float
    this_month: float
    this_year: float


class InventoryReport(BaseModel):
    total_products: int
    in_stock: int
    low_stock: int
    out_of_stock: int
    inventory_value: float