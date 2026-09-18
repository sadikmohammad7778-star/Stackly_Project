from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_companies: int
    total_users: int
    total_categories: int
    total_products: int
    total_sales: int
    total_revenue: float
    low_stock_products: int
    out_of_stock_products: int


class CategorySales(BaseModel):
    category_name: str
    total_sales: float


class MonthlySales(BaseModel):
    month: str
    revenue: float


class TopProduct(BaseModel):
    product_name: str
    quantity_sold: int