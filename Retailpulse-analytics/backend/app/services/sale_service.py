from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product
from app.models.category import Category

from app.schemas.sale_schema import (
    SaleCreate,
    SaleUpdate,
    SalesSummary,
)


# --------------------------------------------------
# Generate Invoice Number
# --------------------------------------------------
def generate_invoice_number(db: Session):

    latest_sale = db.query(Sale).order_by(Sale.id.desc()).first()

    if latest_sale:
        try:
            last_number = int(latest_sale.invoice_number.split("-")[-1])
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0

    current_year = datetime.now().year

    return f"INV-{current_year}-{last_number + 1:06d}"


# --------------------------------------------------
# Create Sale
# --------------------------------------------------
def create_sale(
    db: Session,
    sale: SaleCreate,
    created_by: int = None,
):

    invoice_number = generate_invoice_number(db)

    db_sale = Sale(
        company_id=sale.company_id,
        invoice_number=invoice_number,
        customer_name=sale.customer_name,
        sales_channel=sale.sales_channel,
        payment_method=sale.payment_method,
        total_amount=0,
        created_by=created_by,
    )

    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    grand_total = 0

    for item in sale.items:

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if product is None:
            raise Exception("Product not found")

        category = db.query(Category).filter(
            Category.id == item.category_id
        ).first()

        if category is None:
            raise Exception("Category not found")

        if product.stock_quantity < item.quantity:
            raise Exception(
                f"Insufficient stock for product '{product.name}'"
            )

        item_total = (
            (item.quantity * item.unit_price)
            - item.discount
            + item.tax
        )

        sale_item = SaleItem(
            sale_id=db_sale.id,
            product_id=item.product_id,
            category_id=item.category_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount=item.discount,
            tax=item.tax,
            total=item_total,
        )

        db.add(sale_item)

        # Update Inventory
        product.stock_quantity -= item.quantity

        if product.stock_quantity <= 0:
            product.stock_quantity = 0

            if hasattr(product, "status"):
                product.status = "Out of Stock"

        grand_total += item_total

    db_sale.total_amount = grand_total

    db.commit()
    db.refresh(db_sale)

    return db_sale


# --------------------------------------------------
# Get All Sales
# --------------------------------------------------
def get_all_sales(db: Session):
    return db.query(Sale).all()


# --------------------------------------------------
# Get Sale By ID
# --------------------------------------------------
def get_sale_by_id(
    db: Session,
    sale_id: int,
):
    return (
        db.query(Sale)
        .filter(Sale.id == sale_id)
        .first()
    )


# --------------------------------------------------
# Update Sale
# --------------------------------------------------
def update_sale(
    db: Session,
    sale_id: int,
    sale: SaleUpdate,
):

    db_sale = get_sale_by_id(db, sale_id)

    if db_sale is None:
        return None

    update_data = sale.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_sale, key, value)

    db.commit()
    db.refresh(db_sale)

    return db_sale


# --------------------------------------------------
# Delete Sale
# --------------------------------------------------
def delete_sale(
    db: Session,
    sale_id: int,
):

    db_sale = get_sale_by_id(db, sale_id)

    if db_sale is None:
        return None

    db.delete(db_sale)
    db.commit()

    return True


# --------------------------------------------------
# Search Sales
# --------------------------------------------------
def search_sales(
    db: Session,
    keyword: str,
):

    return (
        db.query(Sale)
        .filter(
            (Sale.invoice_number.ilike(f"%{keyword}%")) |
            (Sale.customer_name.ilike(f"%{keyword}%"))
        )
        .all()
    )


# --------------------------------------------------
# Dashboard Summary
# --------------------------------------------------
def sales_summary(db: Session):

    total_sales = db.query(Sale).count()

    total_revenue = (
        db.query(func.sum(Sale.total_amount))
        .scalar()
        or 0
    )

    average_order_value = (
        total_revenue / total_sales
        if total_sales > 0
        else 0
    )

    return SalesSummary(
        total_sales=total_sales,
        total_revenue=total_revenue,
        average_order_value=average_order_value,
    )