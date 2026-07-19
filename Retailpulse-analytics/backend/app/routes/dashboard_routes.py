from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import List


from app.config.database import get_db

from app.schemas.dashboard_schema import (
    DashboardSummary,
    CategorySales,
    MonthlySales,
    TopProduct,
)
from app.services.dashboard_service import (
    get_dashboard_summary,
    get_sales_by_category,
    get_monthly_sales,
    get_top_products,
)
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def dashboard_summary(
    db: Session = Depends(get_db),
):
    return get_dashboard_summary(db)


@router.get(
    "/sales-by-category",
    response_model=List[CategorySales],
)
def sales_by_category(
    db: Session = Depends(get_db),
):
    return get_sales_by_category(db)


@router.get(
    "/monthly-sales",
    response_model=List[MonthlySales],
)
def monthly_sales(
    db: Session = Depends(get_db),
):
    return get_monthly_sales(db)


@router.get(
    "/top-products",
    response_model=List[TopProduct],
)
def top_products(
    db: Session = Depends(get_db),
):
    return get_top_products(db)