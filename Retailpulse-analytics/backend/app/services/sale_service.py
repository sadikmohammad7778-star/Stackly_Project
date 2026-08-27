from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.services.notification_service import create_notification
from app.services.audit_service import create_audit_log

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product
from app.models.category import Category
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.company import Company

from app.schemas.sale_schema import (
    SaleCreate,
    SaleUpdate,
    SalesSummary,
)


# ============================================================
# Helpers
# ============================================================

def calculate_stock_status(
    available_stock: int,
    reorder_level: int,
) -> str:

    if available_stock <= 0:
        return "Out of Stock"

    if available_stock <= reorder_level:
        return "Low Stock"

    return "In Stock"


def get_product_price(product: Product) -> float:
    price = float(product.unit_price)

    if price <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Product '{product.name}' "
                "has an invalid unit price."
            )
        )

    return price


def generate_invoice_number(
    db: Session,
    company_id: int,
) -> str:

    current_year = datetime.utcnow().year

    latest_sale = (
        db.query(Sale)
        .filter(
            Sale.company_id == company_id,
            Sale.invoice_number.like(
                f"INV-{current_year}-%"
            )
        )
        .order_by(Sale.id.desc())
        .first()
    )

    if latest_sale:
        try:
            last_number = int(
                latest_sale.invoice_number.split("-")[-1]
            )
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0

    return (
        f"INV-{current_year}-{last_number + 1:06d}"
    )


def get_inventory_for_product(
    db: Session,
    company_id: int,
    product_id: int,
) -> Inventory:

    inventory = (
        db.query(Inventory)
        .filter(
            Inventory.company_id == company_id,
            Inventory.product_id == product_id,
        )
        .with_for_update()
        .first()
    )

    if inventory is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Inventory not found for product "
                f"{product_id}."
            ),
        )

    return inventory


def build_sale_response(
    db: Session,
    sale: Sale,
):
    items = []

    for item in sale.items:

        product = (
            db.query(Product)
            .filter(
                Product.id == item.product_id
            )
            .first()
        )

        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": (
                product.name
                if product
                else "Unknown Product"
            ),
            "sku": (
                product.sku
                if product
                else "N/A"
            ),
            "category_id": item.category_id,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "discount": float(item.discount or 0),
            "tax": float(item.tax or 0),
            "total": float(item.total),
        })

    return {
        "id": sale.id,
        "company_id": sale.company_id,
        "invoice_number": sale.invoice_number,
        "customer_id": sale.customer_id,
        "customer_name": sale.customer_name,
        "sale_date": sale.sale_date,
        "sales_channel": sale.sales_channel,
        "payment_method": sale.payment_method,
        "discount": float(sale.discount or 0),
        "tax": float(sale.tax or 0),
        "total_amount": float(sale.total_amount),
        "status": sale.status,
        "items": items,
    }

# ============================================================
# Create Sale
# ============================================================
def create_sale(
    db: Session,
    sale: SaleCreate,
    user_id: int,
    company_id: int,
):
    try:

        # ----------------------------------------------------
        # Validate Company Access
        # ----------------------------------------------------

        if sale.company_id != company_id:
            raise HTTPException(
                status_code=403,
                detail="You cannot create a sale for another company.",
            )

        # ----------------------------------------------------
        # Validate Company
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Validate Company
        # ----------------------------------------------------

        company = (
            db.query(Company)
            .filter(Company.id == sale.company_id)
            .with_for_update()
            .first()
        )

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found.",
            )

        # ----------------------------------------------------
        # Validate Customer
        # ----------------------------------------------------

        customer = (
            db.query(Customer)
            .filter(
                Customer.id == sale.customer_id,
                Customer.company_id == sale.company_id,
            )
            .first()
        )

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found.",
            )

        # ----------------------------------------------------
        # Validate Items
        # ----------------------------------------------------

        if not sale.items:
            raise HTTPException(
                status_code=400,
                detail="At least one product is required.",
            )

        # ----------------------------------------------------
        # Generate Invoice Number
        # ----------------------------------------------------

        invoice_number = generate_invoice_number(
            db,
            sale.company_id,
        )

        # ----------------------------------------------------
        # Create Sale Header
        # ----------------------------------------------------

        db_sale = Sale(
            company_id=sale.company_id,
            invoice_number=invoice_number,
            customer_id=customer.id,
            customer_name=(
                f"{customer.first_name} "
                f"{customer.last_name}"
            ),
            sales_channel=sale.sales_channel,
            payment_method=sale.payment_method,
            discount=sale.discount,
            tax=sale.tax,
            total_amount=0,
            status="Paid",
            created_by=user_id,
        )

        db.add(db_sale)

        # Flush gives us sale.id without committing.
        db.flush()

        subtotal = 0

        # ----------------------------------------------------
        # Process Sale Items
        # ----------------------------------------------------

        for item in sale.items:

            product = (
                db.query(Product)
                .filter(
                    Product.id == item.product_id,
                    Product.company_id == sale.company_id,
                    Product.is_active == True,
                )
                .first()
            )

            if product is None:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Product {item.product_id} "
                        f"not found."
                    ),
                )

            # Category
            category = (
                db.query(Category)
                .filter(Category.id == item.category_id)
                .first()
            )

            if category is None:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Category {item.category_id} "
                        f"not found."
                    ),
                )

            # ------------------------------------------------
            # Inventory
            # ------------------------------------------------

            inventory = get_inventory_for_product(
                db=db,
                company_id=sale.company_id,
                product_id=product.id,
            )

            if inventory.available_stock < item.quantity:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Insufficient stock for "
                        f"'{product.name}'. "
                        f"Available stock: "
                        f"{inventory.available_stock}"
                    ),
                )

            # ------------------------------------------------
            # Actual Product Price
            # ------------------------------------------------

            actual_price = get_product_price(product)

            # ------------------------------------------------
            # Line Calculation
            # ------------------------------------------------

            line_subtotal = (
                item.quantity * actual_price
            )


            line_discount = float(item.discount or 0)
            line_tax = float(item.tax or 0)

            if line_discount < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Discount cannot be negative.",
                )

            if line_tax < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Tax cannot be negative.",
                )

            line_total = (
                line_subtotal
                - line_discount
                + line_tax
            )

            if line_total < 0:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Invalid total for "
                        f"'{product.name}'."
                    ),
                )

            # ------------------------------------------------
            # Sale Item
            # ------------------------------------------------

            sale_item = SaleItem(
                sale_id=db_sale.id,
                product_id=product.id,
                category_id=category.id,
                quantity=item.quantity,
                unit_price=actual_price,
                discount=line_discount,
                tax=line_tax,
                total=line_total,
            )

            db.add(sale_item)

            # ------------------------------------------------
            # Inventory Update
            # ------------------------------------------------

            previous_stock = inventory.current_stock
             
            inventory.current_stock = max(
                0,
                inventory.current_stock - item.quantity,
            )

            inventory.available_stock = max(
                0,
                inventory.available_stock - item.quantity,
            )

            inventory.stock_status = (
                calculate_stock_status(
                    inventory.available_stock,
                    inventory.reorder_level,
                )
            )

            product.stock_quantity = inventory.current_stock
            product.status = inventory.stock_status

            # ------------------------------------------------
            # Inventory Movement
            # ------------------------------------------------

            movement = InventoryMovement(
                inventory_id=inventory.id,
                movement_type="OUT",
                quantity_changed=item.quantity,
                previous_quantity=previous_stock,
                updated_quantity=inventory.current_stock,
                reason="Sale",
                remarks=(
                    f"Invoice {invoice_number}"
                ),
                performed_by=user_id,
            )

            db.add(movement)

            subtotal += line_subtotal

            # ------------------------------------------------
            # Stock Notifications
            # ------------------------------------------------

            if inventory.stock_status == "Out of Stock":

                create_notification(
                    db=db,
                    title="Out of Stock",
                    message=(
                        f"{product.name} is now "
                        f"out of stock."
                    ),
                    type="danger",
                )

            elif inventory.stock_status == "Low Stock":

                create_notification(
                    db=db,
                    title="Low Stock",
                    message=(
                        f"{product.name} has only "
                        f"{inventory.available_stock} "
                        f"items available."
                    ),
                    type="warning",
                )

        # ----------------------------------------------------
        # Overall Billing
        # ----------------------------------------------------

        discount = float(sale.discount or 0)
        tax = float(sale.tax or 0)

        if discount < 0:
            raise HTTPException(
                status_code=400,
                detail="Discount cannot be negative.",
            )

        if tax < 0:
            raise HTTPException(
                status_code=400,
                detail="Tax cannot be negative.",
            )

        taxable_amount = max(
            0,
            subtotal - discount,
        )

        grand_total = (
            taxable_amount + tax
        )

        db_sale.total_amount = grand_total

        # ----------------------------------------------------
        # Customer Statistics
        # ----------------------------------------------------

        customer.total_orders = (
            customer.total_orders + 1
        )

        customer.total_spend = (
            customer.total_spend + grand_total
        )

        customer.last_purchase_date = (
            datetime.utcnow()
        )

        # ----------------------------------------------------
        # Audit
        # ----------------------------------------------------

        create_audit_log(
            db=db,
            company_id=db_sale.company_id,
            user_id=user_id,
            module="Sales",
            action="CREATE",
            description=(
                f"Created Sale "
                f"{db_sale.invoice_number}"
            ),
        )

        # ----------------------------------------------------
        # Success Notification
        # ----------------------------------------------------

        create_notification(
                db=db,
                title="New Sale",
                message=(
                    f"Invoice {db_sale.invoice_number} "
                    f"created successfully. "
                    f"Total ₹{db_sale.total_amount:.2f}"
                ),
                type="success",
        )

        db.commit()

        db.refresh(db_sale)

        return db_sale

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to create sale: {str(exc)}"
            ),
        )


# ============================================================
# Get All Sales
# ============================================================

def get_all_sales(
    db: Session,
    company_id: int | None = None,
):
    query = db.query(Sale)

    if company_id is not None:
        query = query.filter(
            Sale.company_id == company_id
        )

    sales = (
        query
        .order_by(Sale.id.desc())
        .all()
    )

    return [
        build_sale_response(db, sale)
        for sale in sales
    ]


# ============================================================
# Get Sale By ID
# ============================================================

def get_sale_by_id(
    db: Session,
    sale_id: int,
    company_id: int | None = None,
):
    query = (
        db.query(Sale)
        .filter(Sale.id == sale_id)
    )

    if company_id is not None:
        query = query.filter(
            Sale.company_id == company_id
        )

    sale = query.first()

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found.",
        )

    # ----------------------------------------------------
    #  detailed invoice response
    # ----------------------------------------------------

    items = []

    for item in sale.items:

        product = (
            db.query(Product)
            .filter(
                Product.id == item.product_id
            )
            .first()
        )

        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": (
                product.name
                if product
                else "Unknown Product"
            ),
            "sku": (
                product.sku
                if product
                else "N/A"
            ),
            "category_id": item.category_id,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "discount": float(item.discount or 0),
            "tax": float(item.tax or 0),
            "total": float(item.total),
        })

    return {
        "id": sale.id,
        "company_id": sale.company_id,
        "invoice_number": sale.invoice_number,
        "customer_id": sale.customer_id,
        "customer_name": sale.customer_name,
        "sale_date": sale.sale_date,
        "sales_channel": sale.sales_channel,
        "payment_method": sale.payment_method,
        "discount": float(sale.discount or 0),
        "tax": float(sale.tax or 0),
        "total_amount": float(sale.total_amount),
        "status": sale.status,
        "items": items,
    }

def get_sale_model_by_id(
    db: Session,
    sale_id: int,
    company_id: int | None = None,
):
    query = (
        db.query(Sale)
        .filter(Sale.id == sale_id)
    )

    if company_id is not None:
        query = query.filter(
            Sale.company_id == company_id
        )

    sale = query.first()

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found.",
        )

    return sale

# ============================================================
# Update Sale
# ============================================================

def update_sale(
    db: Session,
    sale_id: int,
    sale: SaleUpdate,
    user_id: int,
    company_id: int,
):

    # Get actual SQLAlchemy Sale object
    db_sale = get_sale_model_by_id(
        db=db,
        sale_id=sale_id,
        company_id=company_id,
    )
    update_data = sale.model_dump(
        exclude_unset=True
    )

    try:

        # ----------------------------------------------------
        # Update Customer
        # ----------------------------------------------------

        if "customer_id" in update_data:

            customer = (
                db.query(Customer)
                .filter(
                    Customer.id
                    == update_data["customer_id"],
                    Customer.company_id
                    == db_sale.company_id,
                )
                .first()
            )

            if customer is None:
                raise HTTPException(
                    status_code=404,
                    detail="Customer not found.",
                )

            db_sale.customer_id = customer.id

            db_sale.customer_name = (
                f"{customer.first_name} "
                f"{customer.last_name}"
            )

            update_data.pop("customer_id")

        # ----------------------------------------------------
        # Update Sale Fields
        # ----------------------------------------------------

        for key, value in update_data.items():

            if hasattr(db_sale, key):

                setattr(
                    db_sale,
                    key,
                    value,
                )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        db.commit()

        db.refresh(db_sale)

        # ----------------------------------------------------
        # Audit Log
        # ----------------------------------------------------

        create_audit_log(
            db=db,
            company_id=db_sale.company_id,
            user_id=user_id,
            module="Sales",
            action="UPDATE",
            description=(
                f"Updated Sale "
                f"{db_sale.invoice_number}"
            ),
        )

        return db_sale

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to update sale: {str(exc)}"
            ),
        )
# ============================================================
# Delete Sale
# ============================================================

def delete_sale(
    db: Session,
    sale_id: int,
    user_id: int,
    company_id: int,
):

    db_sale = get_sale_model_by_id(
        db=db,
        sale_id=sale_id,
        company_id=company_id,
    )

    try:

        # ----------------------------------------------------
        # Restore Inventory
        # ----------------------------------------------------

        for item in db_sale.items:

            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.product_id == item.product_id,
                    Inventory.company_id == db_sale.company_id,
                )
                .with_for_update()
                .first()
            )

            if inventory:

                previous_stock = inventory.current_stock

                inventory.current_stock += item.quantity

                inventory.available_stock += item.quantity

                inventory.stock_status = calculate_stock_status(
                    inventory.available_stock,
                    inventory.reorder_level,
                )

                # --------------------------------------------
                # Keep Product synchronized with Inventory
                # --------------------------------------------

                product = (
                    db.query(Product)
                    .filter(
                        Product.id == item.product_id
                    )
                    .first()
                )

                if product:
                    product.stock_quantity = (
                        inventory.current_stock
                    )

                    product.status = (
                        inventory.stock_status
                    )

                # --------------------------------------------
                # Inventory Movement
                # --------------------------------------------

                movement = InventoryMovement(
                    inventory_id=inventory.id,
                    movement_type="IN",
                    quantity_changed=item.quantity,
                    previous_quantity=previous_stock,
                    updated_quantity=inventory.current_stock,
                    reason="Sale Cancellation",
                    remarks=(
                        f"Cancelled invoice "
                        f"{db_sale.invoice_number}"
                    ),
                    performed_by=user_id,
                )

                db.add(movement)

        # ----------------------------------------------------
        # Restore Customer Statistics
        # ----------------------------------------------------

        customer = (
            db.query(Customer)
            .filter(
                Customer.id == db_sale.customer_id
            )
            .first()
        )

        if customer:

            customer.total_orders = max(
                0,
                customer.total_orders - 1,
            )

            customer.total_spend = max(
                0,
                customer.total_spend
                - db_sale.total_amount,
            )

        # ----------------------------------------------------
        # Save information before deletion
        # ----------------------------------------------------

        company_id = db_sale.company_id
        invoice_number = db_sale.invoice_number
        deleted_sale_id = db_sale.id

        # ----------------------------------------------------
        # Audit Log
        # ----------------------------------------------------

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Sales",
            action="DELETE",
            description=(
                f"Deleted Sale "
                f"{invoice_number}"
            ),
        )

        # ----------------------------------------------------
        # Delete Sale
        # ----------------------------------------------------

        db.delete(db_sale)

        # ----------------------------------------------------
        # Commit Everything
        # ----------------------------------------------------

        db.commit()

        return True

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to delete sale: {str(exc)}"
            ),
        )

# ============================================================
# Search Sales
# ============================================================

def search_sales(
    db: Session,
    keyword: str | None = None,
    company_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    payment_method: str | None = None,
    status: str | None = None,
    sort: str = "date",
    order: str = "desc",
):
    query = db.query(Sale)

    # --------------------------------------------------
    # Company Filter
    # --------------------------------------------------

    if company_id is not None:
        query = query.filter(
            Sale.company_id == company_id
        )

    # --------------------------------------------------
    # Search
    # Invoice Number / Customer Name
    # --------------------------------------------------

    if keyword:
        query = query.filter(
            or_(
                Sale.invoice_number.ilike(
                    f"%{keyword}%"
                ),
                Sale.customer_name.ilike(
                    f"%{keyword}%"
                ),
            )
        )

    # --------------------------------------------------
    # Date Range
    # --------------------------------------------------

    if start_date:
        query = query.filter(
            Sale.sale_date >= start_date
        )

    if end_date:
        query = query.filter(
            Sale.sale_date <= end_date
        )

    # --------------------------------------------------
    # Payment Method
    # --------------------------------------------------

    if payment_method:
        query = query.filter(
            Sale.payment_method == payment_method
        )

    # --------------------------------------------------
    # Payment Status
    # --------------------------------------------------

    if status:
        query = query.filter(
            Sale.status == status
        )

    # --------------------------------------------------
    # Sorting
    # --------------------------------------------------

    sort_column = {
        "date": Sale.sale_date,
        "total": Sale.total_amount,
        "customer": Sale.customer_name,
    }.get(sort)

    if sort_column is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort field. "
                "Use: date, total, or customer."
            ),
        )

    if order.lower() == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # --------------------------------------------------
    # Get Sales
    # --------------------------------------------------

    sales = query.all()

    # --------------------------------------------------
    # Build Detailed Response
    # --------------------------------------------------

    return [
        build_sale_response(
            db=db,
            sale=sale,
        )
        for sale in sales
    ]
# ============================================================
# Sales Summary
# ============================================================

def sales_summary(
    db: Session,
    company_id: int | None = None,
):

    query = db.query(Sale)

    if company_id is not None:
        query = query.filter(
            Sale.company_id == company_id
        )

    total_sales = query.count()

    revenue_query = db.query(
        func.sum(Sale.total_amount)
    )

    if company_id is not None:
        revenue_query = revenue_query.filter(
            Sale.company_id == company_id
        )

    total_revenue = (
        revenue_query.scalar()
        or 0
    )

    average_order_value = (
        total_revenue / total_sales
        if total_sales > 0
        else 0
    )

    return SalesSummary(
        total_sales=total_sales,
        total_revenue=float(total_revenue),
        average_order_value=float(
            average_order_value
        ),
    )