from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# -----------------------------
# Generate Forecast Request
# -----------------------------

class ForecastGenerateRequest(BaseModel):
    forecast_period: str


# -----------------------------
# Product Forecast Response
# -----------------------------

class ProductForecastResponse(BaseModel):
    id: int
    product_id: int
    product_name: str

    category_id: int
    category_name: str

    current_stock: int

    historical_sales: float

    predicted_demand: float

    confidence_score: float

    forecast_period: str

    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Category Forecast Response
# -----------------------------

class CategoryForecastResponse(BaseModel):
    category_id: int

    category_name: str

    total_historical_sales: float

    predicted_demand: float

    expected_growth_percentage: float

    forecast_period: str


# -----------------------------
# Dashboard KPI Response
# -----------------------------

class ForecastDashboardResponse(BaseModel):
    total_predicted_demand: float

    products_expected_to_run_out: int

    high_growth_products: int

    slow_moving_products: int

    forecast_accuracy: float


# -----------------------------
# Recommendation Response
# -----------------------------

class ForecastRecommendationResponse(BaseModel):
    product_id: int

    product_name: str

    current_stock: int

    reorder_level: int

    predicted_demand: float

    recommendation: str


# -----------------------------
# Forecast History
# -----------------------------

class ForecastHistoryResponse(BaseModel):
    historical_sales: float

    prediction: float

    accuracy: float

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)