from typing import Optional


DEFAULT_LEAD_TIME_DAYS = 7
DEFAULT_SAFETY_STOCK_PERCENTAGE = 0.20
DEFAULT_FORECAST_DAYS = 30


def calculate_average_daily_demand(
    daily_sales: list[float],
) -> float:
    """Calculate average daily demand from actual daily sales."""

    if not daily_sales:
        return 0.0

    return round(sum(daily_sales) / len(daily_sales), 2)


def calculate_forecasted_demand(
    average_daily_demand: float,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
) -> float:
    """Forecast demand for the requested number of days."""

    if average_daily_demand <= 0:
        return 0.0

    return round(
        average_daily_demand * forecast_days,
        2,
    )


def calculate_days_of_stock_remaining(
    current_stock: float,
    average_daily_demand: float,
) -> Optional[float]:
    """Calculate how many days current stock can support."""

    if average_daily_demand <= 0:
        return None

    return round(
        max(current_stock, 0) / average_daily_demand,
        2,
    )


def calculate_safety_stock(
    average_daily_demand: float,
    lead_time_days: int = DEFAULT_LEAD_TIME_DAYS,
    safety_stock_percentage: float = DEFAULT_SAFETY_STOCK_PERCENTAGE,
) -> float:
    """
    Safety Stock =
    Average Daily Demand × Lead Time × Safety Stock %
    """

    if average_daily_demand <= 0:
        return 0.0

    return round(
        average_daily_demand
        * lead_time_days
        * safety_stock_percentage,
        2,
    )


def calculate_reorder_point(
    average_daily_demand: float,
    lead_time_days: int = DEFAULT_LEAD_TIME_DAYS,
    safety_stock: Optional[float] = None,
) -> float:
    """
    Reorder Point =
    Average Daily Demand × Lead Time + Safety Stock
    """

    if average_daily_demand <= 0:
        return 0.0

    if safety_stock is None:
        safety_stock = calculate_safety_stock(
            average_daily_demand,
            lead_time_days,
        )

    return round(
        (average_daily_demand * lead_time_days)
        + safety_stock,
        2,
    )


def calculate_recommended_reorder_quantity(
    current_stock: float,
    forecasted_demand: float,
    safety_stock: float,
) -> float:
    """
    Recommended Quantity =
    Forecasted Demand + Safety Stock - Current Stock
    """

    target_stock = forecasted_demand + safety_stock

    return round(
        max(target_stock - current_stock, 0),
        2,
    )


def classify_stock_risk(
    current_stock: float,
    average_daily_demand: float,
    days_of_stock_remaining: Optional[float],
    reorder_point: float,
    forecasted_demand: float,
) -> str:
    """Classify inventory risk dynamically."""

    if current_stock <= 0:
        return "Out of Stock"

    if average_daily_demand <= 0:
        return "Overstock"
    if (
        days_of_stock_remaining is not None
        and days_of_stock_remaining <= DEFAULT_LEAD_TIME_DAYS
    ):
        return "Stockout Risk"

    if current_stock < reorder_point:
        return "Low Stock"

    if (
        forecasted_demand > 0
        and current_stock > forecasted_demand * 2
    ):
        return "Overstock"

    return "Healthy"


def generate_recommendation(
    stock_risk: str,
    recommended_reorder_quantity: float,
) -> str:
    """Generate an actionable inventory recommendation."""

    if stock_risk == "Out of Stock":
        return "Immediate Restock Required"

    if stock_risk == "Stockout Risk":
        return "Urgent Reorder Required"

    if stock_risk == "Low Stock":
        if recommended_reorder_quantity > 0:
            return "Reorder Soon"
        return "Monitor Stock"

    if stock_risk == "Overstock":
        return "Reduce Inventory"

    return "Stock Level Healthy"