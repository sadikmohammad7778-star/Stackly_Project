from datetime import datetime
from statistics import mean
import csv
from io import StringIO

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.category import Category
from app.models.demand_forecast import DemandForecast
from app.models.forecast_history import ForecastHistory
from app.models.inventory import Inventory
from app.utils.forecasting import inventory_recommendation
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.utils.forecasting import (
    calculate_predicted_demand,
    calculate_confidence_score,
    calculate_growth,
    inventory_recommendation,
)

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

def generate_forecasts(
    db: Session,
    company_id: int,
    user_id: int,
    forecast_period: str,
):
    """
    Generate demand forecasts for all active products
    belonging to the given company.
    """

    products = (
        db.query(Product)
        .filter(
            Product.company_id == company_id,
            Product.is_active == True,
        )
        .all()
    )

    generated = []

    for product in products:

        # Skip duplicate forecast
        existing = (
            db.query(DemandForecast)
            .filter(
                DemandForecast.company_id == company_id,
                DemandForecast.product_id == product.id,
                DemandForecast.forecast_period == forecast_period,
            )
            .first()
        )

        if existing:
            continue

        # Get historical sales
        sales = (
            db.query(SaleItem.quantity)
            .join(Sale)
            .filter(
                Sale.company_id == company_id,
                SaleItem.product_id == product.id,
            )
            .all()
        )

        sales_history = [sale.quantity for sale in sales]

        # Skip products without sales history
        if not sales_history:
            continue

        # Calculate prediction
        predicted = calculate_predicted_demand(
            sales_history,
            forecast_period,
        )

        confidence = calculate_confidence_score(
            sales_history,
        )

        # Save forecast
        forecast = DemandForecast(
            company_id=company_id,
            product_id=product.id,
            category_id=product.category_id,
            forecast_period=forecast_period,
            predicted_demand=predicted,
            confidence_score=confidence,
        )

        db.add(forecast)
        db.flush()

        # Save forecast history
        history = ForecastHistory(
            forecast_id=forecast.id,
            historical_sales=mean(sales_history),
            prediction=predicted,
            accuracy=confidence,
        )

        db.add(history)

        generated.append(forecast)

    db.commit()

    # Generate notifications
    generate_forecast_notifications(
        db=db,
        company_id=company_id,
    )

    # Create audit log
    create_forecast_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        action="Forecast Generated",
        description=(
            f"{len(generated)} forecasts generated "
            f"for {forecast_period}."
        ),
    )

    return generated


def get_dashboard(
    db: Session,
    company_id: int,
):
    forecasts = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.company_id == company_id
        )
        .all()
    )

    total_predicted = sum(
        f.predicted_demand
        for f in forecasts
    )

    run_out = 0
    high_growth = 0
    slow = 0

    accuracy = []

    for forecast in forecasts:

        product = (
            db.query(Product)
            .filter(
                Product.id == forecast.product_id
            )
            .first()
        )

        if product.stock_quantity < forecast.predicted_demand:
            run_out += 1

        if forecast.predicted_demand > product.stock_quantity * 1.5:
            high_growth += 1

        if forecast.predicted_demand < 10:
            slow += 1

        accuracy.append(
            forecast.confidence_score
        )

    return {
        "total_predicted_demand": total_predicted,
        "products_expected_to_run_out": run_out,
        "high_growth_products": high_growth,
        "slow_moving_products": slow,
        "forecast_accuracy": round(
            mean(accuracy),
            2,
        ) if accuracy else 0,
    }

def get_product_forecasts(
    db: Session,
    company_id: int,
):
    forecasts = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.company_id == company_id
        )
        .all()
    )

    result = []

    for forecast in forecasts:

        product = (
            db.query(Product)
            .filter(
                Product.id == forecast.product_id
            )
            .first()
        )

        category = (
            db.query(Category)
            .filter(
                Category.id == forecast.category_id
            )
            .first()
        )

        history = (
            db.query(ForecastHistory)
            .filter(
                ForecastHistory.forecast_id == forecast.id
            )
            .first()
        )

        result.append({
            "id": forecast.id,
            "product_id": product.id,
            "product_name": product.name,
            "category_id": category.id,
            "category_name": category.name,
            "current_stock": product.stock_quantity,
            "historical_sales": history.historical_sales,
            "predicted_demand": forecast.predicted_demand,
            "confidence_score": forecast.confidence_score,
            "forecast_period": forecast.forecast_period,
            "generated_at": forecast.generated_at,
        })

    return result


def get_category_forecasts(
    db: Session,
    company_id: int,
):
    """
    Returns category-wise demand forecast summary.
    """

    forecasts = (
        db.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.sum(DemandForecast.predicted_demand).label("predicted_demand"),
        )
        .join(
            DemandForecast,
            DemandForecast.category_id == Category.id,
        )
        .filter(
            DemandForecast.company_id == company_id,
        )
        .group_by(
            Category.id,
            Category.name,
        )
        .all()
    )

    result = []

    for forecast in forecasts:

        historical_sales = (
            db.query(
                func.sum(SaleItem.quantity)
            )
            .join(
                Sale,
                Sale.id == SaleItem.sale_id,
            )
            .filter(
                Sale.company_id == company_id,
                SaleItem.category_id == forecast.category_id,
            )
            .scalar()
        ) or 0

        if historical_sales == 0:
            growth = 0
        else:
            growth = round(
                (
                    (
                        forecast.predicted_demand
                        - historical_sales
                    )
                    / historical_sales
                )
                * 100,
                2,
            )

        latest_period = (
            db.query(DemandForecast.forecast_period)
            .filter(
                DemandForecast.company_id == company_id,
                DemandForecast.category_id == forecast.category_id,
            )
            .order_by(
                DemandForecast.generated_at.desc()
            )
            .first()
        )

        result.append(
            {
                "category_id": forecast.category_id,
                "category_name": forecast.category_name,
                "total_historical_sales": historical_sales,
                "predicted_demand": round(
                    forecast.predicted_demand,
                    2,
                ),
                "expected_growth_percentage": growth,
                "forecast_period": latest_period[0]
                if latest_period
                else None,
            }
        )

    return result


def get_inventory_recommendations(
    db: Session,
    company_id: int,
):


    forecasts = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.company_id == company_id
        )
        .all()
    )

    recommendations = []

    for forecast in forecasts:

        product = (
            db.query(Product)
            .filter(
                Product.id == forecast.product_id,
                Product.company_id == company_id,
            )
            .first()
        )

        if not product:
            continue

        inventory = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == product.id
            )
            .first()
        )

        if not inventory:
            continue

        recommendation = inventory_recommendation(
            current_stock=inventory.available_stock,
            reorder_level=inventory.reorder_level,
            predicted_demand=forecast.predicted_demand,
        )

        recommendations.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": inventory.available_stock,
                "reorder_level": inventory.reorder_level,
                "predicted_demand": forecast.predicted_demand,
                "recommendation": recommendation,
            }
        )

    priority = {
        "Immediate Restock Required": 1,
        "Reorder Soon": 2,
        "Stock Level Healthy": 3,
        "Overstock Risk": 4,
    }

    recommendations.sort(
        key=lambda x: priority.get(
            x["recommendation"],
            99,
        )
    )

    return recommendations




def get_chart_data(
    db: Session,
    company_id: int,
):
    """
    Returns all chart data for Demand Forecast Dashboard.
    """

    # -----------------------------
    # Historical Sales vs Forecast
    # -----------------------------

    historical_vs_forecast = (
        db.query(
            Product.name.label("product"),
            func.coalesce(func.sum(SaleItem.quantity), 0).label(
                "historical_sales"
            ),
            func.coalesce(
                func.sum(DemandForecast.predicted_demand), 0
            ).label("forecast"),
        )
        .join(
            SaleItem,
            SaleItem.product_id == Product.id,
        )
        .join(
            Sale,
            Sale.id == SaleItem.sale_id,
        )
        .outerjoin(
            DemandForecast,
            DemandForecast.product_id == Product.id,
        )
        .filter(
            Product.company_id == company_id,
            Sale.company_id == company_id,
        )
        .group_by(Product.name)
        .all()
    )

    # -----------------------------
    # Product Demand Trend
    # -----------------------------

    product_trend = (
        db.query(
            Product.name,
            func.sum(
                DemandForecast.predicted_demand
            ).label("predicted"),
        )
        .join(
            DemandForecast,
            DemandForecast.product_id == Product.id,
        )
        .filter(
            Product.company_id == company_id,
        )
        .group_by(Product.name)
        .all()
    )

    # -----------------------------
    # Category Demand Trend
    # -----------------------------

    category_trend = (
        db.query(
            Category.name,
            func.sum(
                DemandForecast.predicted_demand
            ).label("predicted"),
        )
        .join(
            DemandForecast,
            DemandForecast.category_id == Category.id,
        )
        .filter(
            DemandForecast.company_id == company_id,
        )
        .group_by(Category.name)
        .all()
    )

    # -----------------------------
    # Top Predicted Products
    # -----------------------------

    top_products = (
        db.query(
            Product.name,
            DemandForecast.predicted_demand,
        )
        .join(
            DemandForecast,
            DemandForecast.product_id == Product.id,
        )
        .filter(
            Product.company_id == company_id,
        )
        .order_by(
            DemandForecast.predicted_demand.desc()
        )
        .limit(10)
        .all()
    )

    # -----------------------------
    # Seasonal Sales Pattern
    # -----------------------------

    seasonal_pattern = (
        db.query(
            func.extract(
                "month",
                Sale.sale_date,
            ).label("month"),

            func.sum(
                SaleItem.quantity
            ).label("sales"),
        )
        .join(
            SaleItem,
            SaleItem.sale_id == Sale.id,
        )
        .filter(
            Sale.company_id == company_id,
        )
        .group_by(
            func.extract(
                "month",
                Sale.sale_date,
            )
        )
        .order_by(
            func.extract(
                "month",
                Sale.sale_date,
            )
        )
        .all()
    )

    return {

        "historical_vs_forecast": [
            {
                "product": row.product,
                "historical_sales": row.historical_sales,
                "forecast": row.forecast,
            }
            for row in historical_vs_forecast
        ],

        "product_trend": [
            {
                "product": row.name,
                "predicted": row.predicted,
            }
            for row in product_trend
        ],

        "category_trend": [
            {
                "category": row.name,
                "predicted": row.predicted,
            }
            for row in category_trend
        ],

        "top_products": [
            {
                "product": row.name,
                "predicted": row.predicted_demand,
            }
            for row in top_products
        ],

        "seasonal_pattern": [
            {
                "month": int(row.month),
                "sales": row.sales,
            }
            for row in seasonal_pattern
        ],
    }

def export_forecast_csv(
    db: Session,
    company_id: int,
):
    """
    Export Demand Forecast Report as CSV.
    """

    forecasts = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.company_id == company_id
        )
        .all()
    )

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Product",
        "Category",
        "Forecast Period",
        "Predicted Demand",
        "Confidence Score",
        "Generated At",
    ])

    for forecast in forecasts:

        product = (
            db.query(Product)
            .filter(
                Product.id == forecast.product_id
            )
            .first()
        )

        category = (
            db.query(Category)
            .filter(
                Category.id == forecast.category_id
            )
            .first()
        )

        writer.writerow([
            product.name if product else "",
            category.name if category else "",
            forecast.forecast_period,
            forecast.predicted_demand,
            forecast.confidence_score,
            forecast.generated_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ])

    output.seek(0)

    return output.getvalue()


def export_forecast_pdf(
    db: Session,
    company_id: int,
):
    """
    Export Product Forecast Report as PDF.
    """

    forecasts = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.company_id == company_id
        )
        .order_by(DemandForecast.generated_at.desc())
        .all()
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "<b>Demand Forecast Report</b>",
        styles["Title"],
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    generated = Paragraph(
        f"Generated On : {datetime.utcnow().strftime('%d-%m-%Y %H:%M')}",
        styles["Normal"],
    )

    elements.append(generated)
    elements.append(Spacer(1, 20))

    table_data = [
        [
            "Product",
            "Category",
            "Forecast",
            "Period",
            "Confidence",
        ]
    ]

    for forecast in forecasts:

        product = (
            db.query(Product)
            .filter(
                Product.id == forecast.product_id
            )
            .first()
        )

        category = (
            db.query(Category)
            .filter(
                Category.id == forecast.category_id
            )
            .first()
        )

        table_data.append(
            [
                product.name if product else "-",
                category.name if category else "-",
                str(round(forecast.predicted_demand, 2)),
                forecast.forecast_period,
                f"{forecast.confidence_score:.2f} %",
            ]
        )

    table = Table(table_data)

    table.setStyle(
        TableStyle(
            [

                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86DE")),

                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

                ("ALIGN", (0, 0), (-1, -1), "CENTER"),

                ("GRID", (0, 0), (-1, -1), 1, colors.black),

                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

            ]
        )
    )

    elements.append(table)

    document.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf


def refresh_forecasts(
    db: Session,
    company_id: int,
    user_id: int,
    forecast_period: str,
):
    """
    Refresh demand forecasts for the given company.
    Old forecasts for the selected period are removed
    and regenerated using the latest sales data.
    """

    old_forecasts = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.company_id == company_id,
            DemandForecast.forecast_period == forecast_period,
        )
        .all()
    )

    deleted_count = len(old_forecasts)

    for forecast in old_forecasts:
        db.delete(forecast)

    db.commit()

    new_forecasts = generate_forecasts(
        db=db,
        company_id=company_id,
        user_id=user_id,
        forecast_period=forecast_period,
    )

    create_forecast_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        action="Forecast Refreshed",
        description=(
            f"Forecasts refreshed for "
            f"{forecast_period}. "
            f"{len(new_forecasts)} forecasts generated."
        ),
    )

    return {
        "message": "Forecasts refreshed successfully.",
        "forecast_period": forecast_period,
        "deleted_forecasts": deleted_count,
        "generated_forecasts": len(new_forecasts),
    }
def generate_forecast_notifications(
    db: Session,
    company_id: int,
):
    """
    Generate forecast notifications without creating duplicates.
    """

    forecasts = (
        db.query(DemandForecast)
        .filter(
            DemandForecast.company_id == company_id
        )
        .all()
    )

    notifications_created = 0

    for forecast in forecasts:

        product = (
            db.query(Product)
            .filter(
                Product.id == forecast.product_id
            )
            .first()
        )

        inventory = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == forecast.product_id
            )
            .first()
        )

        if not product or not inventory:
            continue

        title = None
        message = None
        notification_type = None

        # ---------------------------------
        # Immediate Restock
        # ---------------------------------

        if inventory.available_stock == 0:

            title = "Immediate Restock Required"
            message = f"{product.name} is out of stock."
            notification_type = "warning"

        # ---------------------------------
        # Reorder Soon
        # ---------------------------------

        elif forecast.predicted_demand > inventory.available_stock:

            title = "Reorder Soon"
            message = (
                f"{product.name} demand is higher than "
                f"available inventory."
            )
            notification_type = "warning"

        # ---------------------------------
        # High Growth
        # ---------------------------------

        elif forecast.predicted_demand >= (
            inventory.available_stock * 1.5
        ):

            title = "High Demand Product"
            message = (
                f"{product.name} is expected to experience "
                f"significant demand growth."
            )
            notification_type = "info"

        else:
            continue

        # ---------------------------------
        # Duplicate Check
        # ---------------------------------

        existing = (
            db.query(Notification)
            .filter(
                Notification.title == title,
                Notification.message == message,
                Notification.is_read == False,
            )
            .first()
        )

        if existing:
            continue

        notification = Notification(
            title=title,
            message=message,
            type=notification_type,
        )

        db.add(notification)

        notifications_created += 1

    db.commit()

    return {
        "notifications_created": notifications_created
    }

def create_forecast_audit_log(
    db: Session,
    company_id: int,
    user_id: int,
    action: str,
    description: str,
    ip_address: str = None,
    browser: str = None,
):
    """
    Create an audit log entry for the Demand Forecast module.
    """

    audit = AuditLog(
        company_id=company_id,
        user_id=user_id,
        module="Demand Forecast",
        action=action,
        description=description,
        ip_address=ip_address,
        browser=browser,
    )

    db.add(audit)
    db.commit()

    return audit