from typing import Optional

from pydantic import BaseModel


class InventoryForecastResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    category_id: int

    current_stock: int
    average_daily_sales: float
    forecasted_demand: float
    forecast_days: int

    days_of_stock_remaining: Optional[float]

    lead_time_days: int
    safety_stock: float
    reorder_point: float

    recommended_reorder_quantity: float

    stock_risk: str
    recommendation: str

    has_sales_history: bool


class InventoryForecastSummaryResponse(BaseModel):
    products_requiring_reorder: int
    products_at_stockout_risk: int
    overstocked_products: int
    healthy_products: int
    total_products: int