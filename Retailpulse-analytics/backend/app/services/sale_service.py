from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.services.notification_service import create_notification
from app.services.audit_service import create_audit_log

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
    user_id: int,
):

    invoice_number = generate_invoice_number(db)

    db_sale = Sale(
        company_id=sale.company_id,
        invoice_number=invoice_number,
        customer_name=sale.customer_name,
        sales_channel=sale.sales_channel,
        payment_method=sale.payment_method,
        total_amount=0,
        created_by=user_id,
    )

    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    create_audit_log(
    db=db,
    company_id=db_sale.company_id,
    user_id=user_id,
    module="Sales",
    action="CREATE",
    description=f"Created Sale #{db_sale.id}",
)

    grand_total = 0

    for item in sale.items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        category = (
            db.query(Category)
            .filter(Category.id == item.category_id)
            .first()
        )

        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}'"
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

        product.stock_quantity -= item.quantity

        if product.stock_quantity <= 0:
            product.stock_quantity = 0

            if hasattr(product, "status"):
                product.status = "Out of Stock"

            create_notification(
                db=db,
                title="Out of Stock",
                message=f"{product.name} is out of stock.",
                type="danger",
            )

        elif product.stock_quantity <= 10:

            create_notification(
                db=db,
                title="Low Stock",
                message=f"{product.name} has only {product.stock_quantity} items left.",
                type="warning",
            )

        grand_total += item_total

    db_sale.total_amount = grand_total

    db.commit()
    db.refresh(db_sale)


    create_notification(
        db=db,
        title="New Sale",
        message=f"Invoice {db_sale.invoice_number} created successfully. Total ₹{db_sale.total_amount}",
        type="success",
    )

    return db_sale



# --------------------------------------------------
# Get All Sales
# --------------------------------------------------
def get_all_sales(db: Session):
    return (
        db.query(Sale)
        .order_by(Sale.id.desc())
        .all()
    )


# --------------------------------------------------
# Get Sale By ID
# --------------------------------------------------
def get_sale_by_id(
    db: Session,
    sale_id: int,
):
    sale = (
        db.query(Sale)
        .filter(Sale.id == sale_id)
        .first()
    )

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found",
        )

    return sale

# Update Sale
def update_sale(
    db: Session,
    sale_id: int,
    sale: SaleUpdate,
    user_id: int,
):

    db_sale = get_sale_by_id(db, sale_id)

    if db_sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )

    update_data = sale.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_sale, key, value)

    db.commit()
    db.refresh(db_sale)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        module="Sales",
    )
    create_audit_log(
        db=db,
        company_id=sale.company_id,
        user_id=user_id,
        module="Sales",
        action="UPDATE",
        description=f"Updated Sale #{sale.id}",
    )

    return db_sale
# Delete Sale

def delete_sale(
    db: Session,
    sale_id: int,
    user_id: int,
):

    db_sale = get_sale_by_id(db, sale_id)

    if db_sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )

    # Save values before deleting
    company_id = db_sale.company_id
    deleted_sale_id = db_sale.id

    db.delete(db_sale)
    db.commit()

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Sales",
        action="DELETE",
        description=f"Deleted Sale #{deleted_sale_id}",
    )

    return True

# Search Sales

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