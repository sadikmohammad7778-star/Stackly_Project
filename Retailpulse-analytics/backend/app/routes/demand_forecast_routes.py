from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user

from app.models.user import User

from app.schemas.demand_forecast_schema import (
    ForecastGenerateRequest,
)

from app.services.demand_forecast_service import (
    generate_forecasts,
    get_dashboard,
    get_product_forecasts,
    get_category_forecasts,
    get_inventory_recommendations,
    get_chart_data,
    refresh_forecasts,
)

router = APIRouter(
    prefix="/forecast",
    tags=["Demand Forecast"],
)


# ==========================================
# Generate Forecast
# ==========================================

@router.post("/generate")
def generate_forecast(
    request: ForecastGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    forecasts = generate_forecasts(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        forecast_period=request.forecast_period,
    )

    return {
        "message": "Forecast generated successfully.",
        "generated": len(forecasts),
    }


# ==========================================
# Dashboard
# ==========================================

@router.get("/dashboard")
def forecast_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return get_dashboard(
        db=db,
        company_id=current_user.company_id,
    )


# ==========================================
# Product Forecasts
# ==========================================

@router.get("/products")
def get_products_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return get_product_forecasts(
        db=db,
        company_id=current_user.company_id,
    )


# ==========================================
# Category Forecasts
# ==========================================

@router.get("/categories")
def get_categories_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return get_category_forecasts(
        db=db,
        company_id=current_user.company_id,
    )


# ==========================================
# Inventory Recommendations
# ==========================================

@router.get("/recommendations")
def inventory_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return get_inventory_recommendations(
        db=db,
        company_id=current_user.company_id,
    )


# ==========================================
# Chart Data
# ==========================================

@router.get("/charts")
def forecast_charts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return get_chart_data(
        db=db,
        company_id=current_user.company_id,
    )


# ==========================================
# Refresh Forecast
# ==========================================

@router.post("/refresh")
def refresh_demand_forecast(
    request: ForecastGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return refresh_forecasts(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        forecast_period=request.forecast_period,
    )