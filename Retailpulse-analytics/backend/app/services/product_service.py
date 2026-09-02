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
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    try:
        category = (
            db.query(Category)
            .filter(
                Category.id == product.category_id,
                Category.company_id == company_id,
            )
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found."
            )

        if product.stock_quantity < 0:
            raise HTTPException(
                status_code=400,
                detail="Stock quantity cannot be negative."
            )

        if product.unit_price <= 0:
            raise HTTPException(
                status_code=400,
                detail="Unit price must be greater than zero."
            )

        last_product = (
            db.query(Product)
            .filter(Product.company_id == company_id)
            .order_by(Product.id.desc())
            .first()
        )

        if last_product:
            sku = f"SKU-{last_product.id + 1:05d}"
        else:
            sku = "SKU-00001"

        initial_stock = product.stock_quantity

        if initial_stock <= 0:
            stock_status = "Out of Stock"
        elif initial_stock <= 10:
            stock_status = "Low Stock"
        else:
            stock_status = "In Stock"

        db_product = Product(
            company_id=company_id,
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
        db.flush()

        db_inventory = Inventory(
            company_id=company_id,
            product_id=db_product.id,
            current_stock=initial_stock,
            reserved_stock=0,
            available_stock=initial_stock,
            reorder_level=10,
            stock_status=stock_status,
        )

        db.add(db_inventory)

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Product",
            action="CREATE",
            resource_type="Product",
            resource_id=str(db_product.id),
            description=(
                f"Created product "
                f"'{db_product.name}' "
                f"(SKU: {db_product.sku})"
            ),
            after_values={
                "name": db_product.name,
                "sku": db_product.sku,
                "category_id": db_product.category_id,
                "description": db_product.description,
                "brand": db_product.brand,
                "unit_price": db_product.unit_price,
                "stock_quantity": db_product.stock_quantity,
                "status": db_product.status,
                "is_active": db_product.is_active,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
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
            detail=f"Failed to create product: {str(exc)}"
        )


def get_all_products(
    db: Session,
    search: str = None,
    company_id: int = None,
):
    query = (
        db.query(Product)
        .filter(Product.company_id == company_id)
    )

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    return query.all()


def get_product_by_id(
    db: Session,
    product_id: int,
    company_id: int,
):
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.company_id == company_id,
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return product


def update_product(
    db: Session,
    product_id: int,
    product: ProductUpdate,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    db_product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.company_id == company_id,
        )
        .first()
    )

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    before_values = {
        "name": db_product.name,
        "sku": db_product.sku,
        "category_id": db_product.category_id,
        "description": db_product.description,
        "brand": db_product.brand,
        "unit_price": float(db_product.unit_price),
        "stock_quantity": db_product.stock_quantity,
        "status": db_product.status,
        "is_active": db_product.is_active,
    }

    try:
        update_data = product.model_dump(
            exclude_unset=True
        )

        update_data.pop("company_id", None)

        if (
            "unit_price" in update_data
            and update_data["unit_price"] <= 0
        ):
            raise HTTPException(
                status_code=400,
                detail="Unit price must be greater than zero."
            )

        new_stock = update_data.pop(
            "stock_quantity",
            None
        )

        if "category_id" in update_data:
            category = (
                db.query(Category)
                .filter(
                    Category.id == update_data["category_id"],
                    Category.company_id == company_id,
                )
                .first()
            )

            if not category:
                raise HTTPException(
                    status_code=404,
                    detail="Category not found."
                )

        for key, value in update_data.items():
            setattr(db_product, key, value)

        if new_stock is not None:

            if new_stock < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Stock quantity cannot be negative."
                )

            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.product_id == db_product.id,
                    Inventory.company_id == company_id,
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
                else "Low Stock"
                if inventory.available_stock <= inventory.reorder_level
                else "In Stock"
            )

            db_product.stock_quantity = inventory.current_stock
            db_product.status = inventory.stock_status

        after_values = {
            "name": db_product.name,
            "sku": db_product.sku,
            "category_id": db_product.category_id,
            "description": db_product.description,
            "brand": db_product.brand,
            "unit_price": float(db_product.unit_price),
            "stock_quantity": db_product.stock_quantity,
            "status": db_product.status,
            "is_active": db_product.is_active,
        }

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Product",
            action="UPDATE",
            resource_type="Product",
            resource_id=str(db_product.id),
            description=f"Updated product '{db_product.name}'",
            before_values=before_values,
            after_values=after_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
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


def delete_product(
    db: Session,
    product_id: int,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    db_product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.company_id == company_id,
        )
        .first()
    )

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    product_name = db_product.name
    product_id_value = db_product.id

    before_values = {
        "name": db_product.name,
        "sku": db_product.sku,
        "category_id": db_product.category_id,
        "description": db_product.description,
        "brand": db_product.brand,
        "unit_price": db_product.unit_price,
        "stock_quantity": db_product.stock_quantity,
        "status": db_product.status,
        "is_active": db_product.is_active,
    }

    db.delete(db_product)

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Product",
        action="DELETE",
        resource_type="Product",
        resource_id=str(product_id_value),
        description=f"Deleted product '{product_name}'",
        before_values=before_values,
        after_values=None,
        ip_address=ip_address,
        user_agent=user_agent,
        status="SUCCESS",
    )

    db.commit()

    return {
        "message": "Product deleted successfully."
    }


def search_products(
    db: Session,
    keyword: str,
    company_id: int,
):
    return (
        db.query(Product)
        .filter(
            Product.company_id == company_id,
            or_(
                Product.name.ilike(f"%{keyword}%"),
                Product.sku.ilike(f"%{keyword}%"),
            )
        )
        .all()
    )


def get_products_by_category(
    db: Session,
    category_id: int,
    company_id: int,
):
    return (
        db.query(Product)
        .filter(
            Product.category_id == category_id,
            Product.company_id == company_id,
        )
        .all()
    )


def low_stock_products(
    db: Session,
    company_id: int,
    limit: int = 10,
):
    return (
        db.query(Product)
        .filter(
            Product.company_id == company_id,
            Product.stock_quantity <= limit,
        )
        .all()
    )


def out_of_stock_products(
    db: Session,
    company_id: int,
):
    return (
        db.query(Product)
        .filter(
            Product.company_id == company_id,
            Product.stock_quantity == 0,
        )
        .all()
    )