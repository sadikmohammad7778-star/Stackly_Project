from pydantic import BaseModel


class SalesReport(BaseModel):
    total_sales: int
    total_revenue: float
    average_order_value: float


class StockReport(BaseModel):
    total_products: int
    in_stock: int
    low_stock: int
    out_of_stock: int