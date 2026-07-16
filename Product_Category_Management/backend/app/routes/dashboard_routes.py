from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config.database import get_db
from app.models.product import Product
from app.models.category import Category

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    total_products = db.query(Product).count()

    active_products = (
        db.query(Product)
        .filter(Product.status == "Active")
        .count()
    )

    inactive_products = (
        db.query(Product)
        .filter(Product.status == "Inactive")
        .count()
    )

    total_categories = db.query(Category).count()

    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "total_categories": total_categories,
    }