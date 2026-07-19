from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.sale import Sale
from app.models.product import Product
from app.schemas.report_schema import SalesReport, StockReport


def get_sales_report(db: Session):

    total_sales = db.query(Sale).count()

    total_revenue = (
        db.query(func.sum(Sale.total_amount)).scalar() or 0
    )

    average_order_value = (
        total_revenue / total_sales
        if total_sales > 0
        else 0
    )

    return SalesReport(
        total_sales=total_sales,
        total_revenue=float(total_revenue),
        average_order_value=float(average_order_value),
    )


def get_stock_report(db: Session):

    total_products = db.query(Product).count()

    in_stock = (
        db.query(Product)
        .filter(Product.stock_quantity > 10)
        .count()
    )

    low_stock = (
        db.query(Product)
        .filter(Product.stock_quantity.between(1, 10))
        .count()
    )

    out_of_stock = (
        db.query(Product)
        .filter(Product.stock_quantity == 0)
        .count()
    )

    return StockReport(
        total_products=total_products,
        in_stock=in_stock,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
    )