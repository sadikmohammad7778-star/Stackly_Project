from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db

from app.schemas.analytics_schema import (
    RevenueReport,
    InventoryReport,
    DashboardKPIs,
    RevenueTrendItem,
    TopProductItem,
    TopCategoryItem,
    PaymentMethodItem,
    SalesChannelItem,
    InventoryCategoryItem,
    StockStatusItem,
    InventoryValueItem,
)

from app.services.analytics_service import (
    get_revenue_report,
    get_inventory_report,
    get_dashboard_kpis,
    get_revenue_trend,
    get_top_products,
    get_top_categories,
    get_payment_method_analysis,
    get_sales_channel_analysis,
    get_inventory_by_category,
    get_stock_status_summary,
    get_inventory_value_by_category,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ==========================================================
# Revenue Report
# ==========================================================

@router.get(
    "/revenue",
    response_model=RevenueReport,
)
def revenue_report(
    db: Session = Depends(get_db),
):
    return get_revenue_report(db)


# ==========================================================
# Inventory Report
# ==========================================================

@router.get(
    "/inventory",
    response_model=InventoryReport,
)
def inventory_report(
    db: Session = Depends(get_db),
):
    return get_inventory_report(db)


# ==========================================================
# Dashboard KPIs
# ==========================================================

@router.get(
    "/dashboard",
    response_model=DashboardKPIs,
)
def dashboard(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_dashboard_kpis(
        db,
        company_id,
    )


# ==========================================================
# Revenue Trend
# ==========================================================

@router.get(
    "/revenue-trend",
    response_model=list[RevenueTrendItem],
)
def revenue_trend(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_revenue_trend(
        db,
        company_id,
    )


# ==========================================================
# Top Products
# ==========================================================

@router.get(
    "/top-products",
    response_model=list[TopProductItem],
)
def top_products(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_top_products(
        db,
        company_id,
    )


# ==========================================================
# Top Categories
# ==========================================================

@router.get(
    "/top-categories",
    response_model=list[TopCategoryItem],
)
def top_categories(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_top_categories(
        db,
        company_id,
    )


# ==========================================================
# Payment Methods
# ==========================================================

@router.get(
    "/payment-methods",
    response_model=list[PaymentMethodItem],
)
def payment_methods(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_payment_method_analysis(
        db,
        company_id,
    )


# ==========================================================
# Sales Channels
# ==========================================================

@router.get(
    "/sales-channels",
    response_model=list[SalesChannelItem],
)
def sales_channels(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_sales_channel_analysis(
        db,
        company_id,
    )


# ==========================================================
# Inventory by Category
# ==========================================================

@router.get(
    "/inventory-category",
    response_model=list[InventoryCategoryItem],
)
def inventory_category(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_inventory_by_category(
        db,
        company_id,
    )


# ==========================================================
# Stock Status Summary
# ==========================================================

@router.get(
    "/stock-status",
    response_model=list[StockStatusItem],
)
def stock_status(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_stock_status_summary(
        db,
        company_id,
    )


# ==========================================================
# Inventory Value by Category
# ==========================================================

@router.get(
    "/inventory-value",
    response_model=list[InventoryValueItem],
)
def inventory_value(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_inventory_value_by_category(
        db,
        company_id,
    )