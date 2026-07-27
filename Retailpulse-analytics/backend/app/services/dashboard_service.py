from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.company import Company
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.sale import Sale

from app.schemas.dashboard_schema import DashboardSummary

from app.models.sale_item import SaleItem


def get_sales_by_category(db: Session):

    results = (
        db.query(
            Category.name.label("category_name"),
            func.sum(SaleItem.total).label("total_sales"),
        )
        .join(SaleItem, Category.id == SaleItem.category_id)
        .group_by(Category.name)
        .all()
    )

    return [
        {
            "category_name": row.category_name,
            "total_sales": float(row.total_sales or 0),
        }
        for row in results
    ]


def get_dashboard_summary(db: Session):

    total_companies = db.query(Company).count()

    total_users = db.query(User).count()

    total_categories = db.query(Category).count()

    total_products = db.query(Product).count()

    total_sales = db.query(Sale).count()

    total_revenue = (
        db.query(func.sum(Sale.total_amount))
        .scalar()
        or 0
    )

    low_stock_products = (
        db.query(Product)
        .filter(Product.stock_quantity <= 10)
        .count()
    )

    out_of_stock_products = (
        db.query(Product)
        .filter(Product.stock_quantity == 0)
        .count()
    )

    return DashboardSummary(
        total_companies=total_companies,
        total_users=total_users,
        total_categories=total_categories,
        total_products=total_products,
        total_sales=total_sales,
        total_revenue=total_revenue,
        low_stock_products=low_stock_products,
        out_of_stock_products=out_of_stock_products,
    )

def get_monthly_sales(db: Session):

    results = (
        db.query(
            func.to_char(
                Sale.created_at,
                "YYYY-MM"
            ).label("month"),
            func.sum(Sale.total_amount).label("revenue"),
        )
        .group_by(
            func.to_char(
                Sale.created_at,
                "YYYY-MM"
            )
        )
        .order_by(
            func.to_char(
                Sale.created_at,
                "YYYY-MM"
            )
        )
        .all()
    )

    return [
        {
            "month": row.month,
            "revenue": float(row.revenue or 0),
        }
        for row in results
    ]

def get_top_products(db: Session):

    results = (
        db.query(
            Product.name.label("product_name"),
            func.sum(SaleItem.quantity).label("quantity_sold"),
        )
        .join(SaleItem, Product.id == SaleItem.product_id)
        .group_by(Product.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(10)
        .all()
    )

    return [
        {
            "product_name": row.product_name,
            "quantity_sold": int(row.quantity_sold or 0),
        }
        for row in results
    ]