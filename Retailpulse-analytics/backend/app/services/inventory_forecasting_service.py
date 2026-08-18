from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.sale_item import SaleItem

from app.utils.inventory_forecasting import (
    DEFAULT_FORECAST_DAYS,
    DEFAULT_LEAD_TIME_DAYS,
    calculate_average_daily_demand,
    calculate_forecasted_demand,
    calculate_days_of_stock_remaining,
    calculate_safety_stock,
    calculate_reorder_point,
    calculate_recommended_reorder_quantity,
    classify_stock_risk,
    generate_recommendation,
)


def _get_daily_sales(
    db: Session,
    company_id: int,
    product_id: int,
) -> list[float]:
    """
    Get actual historical sales and aggregate them by date.
    """

    rows = (
        db.query(
            Sale.sale_date,
            SaleItem.quantity,
        )
        .join(
            SaleItem,
            SaleItem.sale_id == Sale.id,
        )
        .filter(
            Sale.company_id == company_id,
            SaleItem.product_id == product_id,
            Sale.status != "Cancelled",
        )
        .order_by(
            Sale.sale_date.asc()
        )
        .all()
    )

    daily_sales = defaultdict(float)

    for sale_date, quantity in rows:

        if not sale_date:
            continue

        day = sale_date.date()

        daily_sales[day] += float(
            quantity or 0
        )

    return list(daily_sales.values())


def _build_product_forecast(
    db: Session,
    product: Product,
    inventory: Inventory,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
    lead_time_days: int = DEFAULT_LEAD_TIME_DAYS,
):
    daily_sales = _get_daily_sales(
        db=db,
        company_id=product.company_id,
        product_id=product.id,
    )

    average_daily_demand = calculate_average_daily_demand(
        daily_sales
    )

    current_stock = float(
        inventory.available_stock or 0
    )

    forecasted_demand = calculate_forecasted_demand(
        average_daily_demand=average_daily_demand,
        forecast_days=forecast_days,
    )

    days_remaining = calculate_days_of_stock_remaining(
        current_stock=current_stock,
        average_daily_demand=average_daily_demand,
    )

    safety_stock = calculate_safety_stock(
        average_daily_demand=average_daily_demand,
        lead_time_days=lead_time_days,
    )

    reorder_point = calculate_reorder_point(
        average_daily_demand=average_daily_demand,
        lead_time_days=lead_time_days,
        safety_stock=safety_stock,
    )

    recommended_quantity = (
        calculate_recommended_reorder_quantity(
            current_stock=current_stock,
            forecasted_demand=forecasted_demand,
            safety_stock=safety_stock,
        )
    )

    stock_risk = classify_stock_risk(
        current_stock=current_stock,
        average_daily_demand=average_daily_demand,
        days_of_stock_remaining=days_remaining,
        reorder_point=reorder_point,
        forecasted_demand=forecasted_demand,
    )

    recommendation = generate_recommendation(
        stock_risk=stock_risk,
        recommended_reorder_quantity=recommended_quantity,
    )

    return {
        "product_id": product.id,
        "product_name": product.name,
        "sku": product.sku,
        "category_id": product.category_id,
        "current_stock": int(current_stock),
        "average_daily_sales": average_daily_demand,
        "forecasted_demand": forecasted_demand,
        "forecast_days": forecast_days,
        "days_of_stock_remaining": days_remaining,
        "lead_time_days": lead_time_days,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "recommended_reorder_quantity": recommended_quantity,
        "stock_risk": stock_risk,
        "recommendation": recommendation,
        "has_sales_history": len(daily_sales) > 0,
    }


def get_inventory_forecast(
    db: Session,
    company_id: int,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
):
    """Return Task 11 forecast data for all active products."""

    products = (
        db.query(Product)
        .filter(
            Product.company_id == company_id,
            Product.is_active == True,
        )
        .all()
    )

    results = []

    for product in products:

        inventory = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product.id,
                Inventory.company_id == company_id,
            )
            .first()
        )

        if not inventory:
            continue

        results.append(
            _build_product_forecast(
                db=db,
                product=product,
                inventory=inventory,
                forecast_days=forecast_days,
            )
        )

    return results


def get_product_inventory_forecast(
    db: Session,
    company_id: int,
    product_id: int,
):
    """Return Task 11 forecast for one product."""

    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.company_id == company_id,
            Product.is_active == True,
        )
        .first()
    )

    if not product:
        return None

    inventory = (
        db.query(Inventory)
        .filter(
            Inventory.product_id == product.id,
            Inventory.company_id == company_id,
        )
        .first()
    )

    if not inventory:
        return None

    return _build_product_forecast(
        db=db,
        product=product,
        inventory=inventory,
    )


def get_recommendation_summary(
    db: Session,
    company_id: int,
):
    """Return dynamic Task 11 summary counts."""

    forecasts = get_inventory_forecast(
        db=db,
        company_id=company_id,
    )

    return {
        "products_requiring_reorder": sum(
            item["recommended_reorder_quantity"] > 0
            for item in forecasts
        ),
        "products_at_stockout_risk": sum(
            item["stock_risk"]
            in ("Out of Stock", "Stockout Risk")
            for item in forecasts
        ),
        "overstocked_products": sum(
            item["stock_risk"] == "Overstock"
            for item in forecasts
        ),
        "healthy_products": sum(
            item["stock_risk"] == "Healthy"
            for item in forecasts
        ),
        "total_products": len(forecasts),
    }