from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.category import Category


def get_dashboard_summary(db: Session):

    total_products = db.query(Product).count()

    active_products = db.query(Product).filter(
        Product.status == "Active"
    ).count()

    inactive_products = db.query(Product).filter(
        Product.status == "Inactive"
    ).count()

    total_categories = db.query(Category).count()

    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "total_categories": total_categories
    }