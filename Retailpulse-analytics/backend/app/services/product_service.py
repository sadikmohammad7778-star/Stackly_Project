from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.models.category import Category
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.services.audit_service import create_audit_log


# -----------------------------
# Create Product
# -----------------------------
def create_product(
    db: Session,
    product: ProductCreate,
    user_id: int,
):
    # Check category exists
    category = (
        db.query(Category)
        .filter(Category.id == product.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    # Generate SKU automatically
    last_product = (
        db.query(Product)
        .order_by(Product.id.desc())
        .first()
    )

    if last_product:
        sku = f"SKU-{last_product.id + 1:05d}"
    else:
        sku = "SKU-00001"

    # Create Product
    db_product = Product(
        company_id=product.company_id,
        category_id=product.category_id,
        name=product.name,
        sku=sku,
        description=product.description,
        brand=product.brand,
        unit_price=product.unit_price,
        stock_quantity=product.stock_quantity,
        status=product.status,
        is_active=product.is_active,
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Audit Log
    create_audit_log(
        db=db,
        company_id=db_product.company_id,
        user_id=user_id,
        module="Product",
        action="CREATE",
        description=f"Created product '{db_product.name}' (SKU: {db_product.sku})",
    )

    return db_product
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


# -----------------------------
# Update Product
# -----------------------------
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

    update_data = product.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    create_audit_log(
        db=db,
        company_id=db_product.company_id,
        user_id=user_id,
        module="Product",
        action="UPDATE",
        description=f"Updated product '{db_product.name}'",
    )

    return db_product


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