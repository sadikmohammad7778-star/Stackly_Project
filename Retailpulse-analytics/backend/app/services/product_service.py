from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.models.category import Category
from app.models.inventory import Inventory
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.services.audit_service import create_audit_log


def create_product(
    db: Session,
    product: ProductCreate,
    user_id: int,
):
    try:
        # ----------------------------------------
        # Check Category
        # ----------------------------------------

        category = (
            db.query(Category)
            .filter(
                Category.id == product.category_id
            )
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found."
            )

        # ----------------------------------------
        # Validate Stock
        # ----------------------------------------

        if product.stock_quantity < 0:
            raise HTTPException(
                status_code=400,
                detail="Stock quantity cannot be negative."
            )

        # ----------------------------------------
        # Validate Price
        # ----------------------------------------

        if product.unit_price <= 0:
            raise HTTPException(
                status_code=400,
                detail="Unit price must be greater than zero."
            )

        # ----------------------------------------
        # Generate SKU
        # ----------------------------------------

        last_product = (
            db.query(Product)
            .order_by(Product.id.desc())
            .first()
        )

        if last_product:
            sku = f"SKU-{last_product.id + 1:05d}"
        else:
            sku = "SKU-00001"

        # ----------------------------------------
        # Determine Initial Stock Status
        # ----------------------------------------

        initial_stock = product.stock_quantity

        if initial_stock <= 0:
            stock_status = "Out of Stock"
        elif initial_stock <= 10:
            stock_status = "Low Stock"
        else:
            stock_status = "In Stock"

        # ----------------------------------------
        # Create Product
        # ----------------------------------------

        db_product = Product(
            company_id=product.company_id,
            category_id=product.category_id,
            name=product.name,
            sku=sku,
            description=product.description,
            brand=product.brand,
            unit_price=product.unit_price,
            stock_quantity=initial_stock,
            status=stock_status,
            is_active=product.is_active,
        )

        db.add(db_product)

        # Get generated Product ID
        db.flush()

        # ----------------------------------------
        # Create Inventory Record
        # ----------------------------------------

        db_inventory = Inventory(
            company_id=product.company_id,
            product_id=db_product.id,
            current_stock=initial_stock,
            reserved_stock=0,
            available_stock=initial_stock,
            reorder_level=10,
            stock_status=stock_status,
        )

        db.add(db_inventory)

        # ----------------------------------------
        # Audit
        # ----------------------------------------

        create_audit_log(
            db=db,
            company_id=db_product.company_id,
            user_id=user_id,
            module="Product",
            action="CREATE",
            description=(
                f"Created product "
                f"'{db_product.name}' "
                f"(SKU: {db_product.sku})"
            ),
        )

        # ----------------------------------------
        # Commit Product + Inventory + Audit
        # ----------------------------------------

        db.commit()

        db.refresh(db_product)

        return db_product

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create product: {str(exc)}"
        )
    
# -----------------------------
# Get All Products
# -----------------------------
def get_all_products(db: Session, search: str = None):
    query = db.query(Product)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    return query.all()


# -----------------------------
# Get Product By ID
# -----------------------------
def get_product_by_id(
    db: Session,
    product_id: int,
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return product

# --------------------
# Update Product
# -------------------
def update_product(
    db: Session,
    product_id: int,
    product: ProductUpdate,
    user_id: int,
):
    db_product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    try:
        update_data = product.model_dump(
            exclude_unset=True
        )

        # ----------------------------------------
        # Validate Price
        # ----------------------------------------

        if (
            "unit_price" in update_data
            and update_data["unit_price"] <= 0
        ):
            raise HTTPException(
                status_code=400,
                detail="Unit price must be greater than zero."
            )

        # ----------------------------------------
        # Handle Stock Separately
        # ----------------------------------------

        new_stock = update_data.pop(
            "stock_quantity",
            None
        )

        # Update normal Product fields
        for key, value in update_data.items():
            setattr(
                db_product,
                key,
                value
            )

        # ----------------------------------------
        # Synchronize Inventory
        # ----------------------------------------

        if new_stock is not None:

            if new_stock < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Stock quantity cannot be negative."
                )

            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.product_id
                    == db_product.id,
                    Inventory.company_id
                    == db_product.company_id,
                )
                .with_for_update()
                .first()
            )

            if inventory is None:
                raise HTTPException(
                    status_code=404,
                    detail="Inventory record not found."
                )

            inventory.current_stock = new_stock

            inventory.available_stock = max(
                0,
                new_stock - inventory.reserved_stock
            )

            inventory.stock_status = (
                "Out of Stock"
                if inventory.available_stock == 0
                else
                "Low Stock"
                if inventory.available_stock
                <= inventory.reorder_level
                else
                "In Stock"
            )

            db_product.stock_quantity = (
                inventory.current_stock
            )

            db_product.status = (
                inventory.stock_status
            )

        # ----------------------------------------
        # Audit
        # ----------------------------------------

        create_audit_log(
            db=db,
            company_id=db_product.company_id,
            user_id=user_id,
            module="Product",
            action="UPDATE",
            description=(
                f"Updated product "
                f"'{db_product.name}'"
            ),
        )

        db.commit()

        db.refresh(db_product)

        return db_product

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to update product: {str(exc)}"
        )
# -----------------------------
# Delete Product
# -----------------------------
def delete_product(
    db: Session,
    product_id: int,
    user_id: int,
):
    db_product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    product_name = db_product.name
    company_id = db_product.company_id

    db.delete(db_product)
    db.commit()

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Product",
        action="DELETE",
        description=f"Deleted product '{product_name}'",
    )

    return {
        "message": "Product deleted successfully."
    }


# -----------------------------
# Search Products
# -----------------------------
def search_products(
    db: Session,
    keyword: str,
):
    return (
        db.query(Product)
        .filter(
            or_(
                Product.name.ilike(f"%{keyword}%"),
                Product.sku.ilike(f"%{keyword}%"),
            )
        )
        .all()
    )


# -----------------------------
# Filter By Category
# -----------------------------
def get_products_by_category(
    db: Session,
    category_id: int,
):
    return (
        db.query(Product)
        .filter(Product.category_id == category_id)
        .all()
    )


# -----------------------------
# Low Stock Products
# -----------------------------
def low_stock_products(
    db: Session,
    limit: int = 10,
):
    return (
        db.query(Product)
        .filter(Product.stock_quantity <= limit)
        .all()
    )


# -----------------------------
# Out Of Stock Products
# -----------------------------
def out_of_stock_products(
    db: Session,
):
    return (
        db.query(Product)
        .filter(Product.stock_quantity == 0)
        .all()
    )