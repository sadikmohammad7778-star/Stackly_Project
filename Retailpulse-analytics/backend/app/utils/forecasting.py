from statistics import mean


def calculate_moving_average(sales_history: list[float]) -> float:
    """
    Calculates the average sales from historical data.
    """

    if not sales_history:
        return 0

    return round(mean(sales_history), 2)


def calculate_predicted_demand(
    sales_history: list[float],
    forecast_period: str,
) -> float:
    """
    Predict future demand based on moving average.
    """

    average_sales = calculate_moving_average(sales_history)

    period_multiplier = {
        "7_days": 7,
        "30_days": 30,
        "90_days": 90,
    }

    days = period_multiplier.get(forecast_period, 30)

    # Assume historical sales are daily average
    predicted = average_sales * days

    return round(predicted, 2)


def calculate_confidence_score(
    sales_history: list[float],
) -> float:
    """
    Confidence based on consistency of historical sales.
    """

    if len(sales_history) < 2:
        return 50

    avg = mean(sales_history)

    max_difference = max(abs(s - avg) for s in sales_history)

    if avg == 0:
        return 50

    confidence = 100 - ((max_difference / avg) * 100)

    confidence = max(50, min(99, confidence))

    return round(confidence, 2)


def calculate_growth(
    historical_sales: float,
    predicted_sales: float,
):
    if historical_sales == 0:
        return 0

    growth = (
        (predicted_sales - historical_sales)
        / historical_sales
    ) * 100

    return round(growth, 2)


def inventory_recommendation(
    current_stock: int,
    reorder_level: int,
    predicted_demand: float,
):
    """
    Inventory Recommendation
    """

    if current_stock == 0:
        return "Immediate Restock Required"

    if current_stock < reorder_level:
        return "Reorder Soon"

    if current_stock < predicted_demand:
        return "Reorder Soon"

    if current_stock > predicted_demand * 2:
        return "Overstock Risk"

    return "Stock Level Healthy"