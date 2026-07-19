from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.models.category import Category
from app.schemas.product_schema import ProductCreate, ProductUpdate


# -----------------------------
# Create Product
# -----------------------------
def create_product(db: Session, product: ProductCreate):

    category = (
        db.query(Category)
        .filter(Category.id == product.category_id)
        .first()
    )

    if not category:
        raise Exception("Category not found")

    db_product = Product(
        company_id=product.company_id,
        category_id=product.category_id,
        name=product.name,
        sku=product.sku,
        description=product.description,
        unit_price=product.unit_price,
        stock_quantity=product.stock_quantity,
        status=product.status,
        is_active=product.is_active,
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

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
def get_product_by_id(db: Session, product_id: int):
    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


# -----------------------------
# Update Product
# -----------------------------
def update_product(
    db: Session,
    product_id: int,
    product: ProductUpdate
):

    db_product = get_product_by_id(db, product_id)

    if not db_product:
        return None

    update_data = product.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    return db_product


# -----------------------------
# Delete Product
# -----------------------------
def delete_product(db: Session, product_id: int):

    db_product = get_product_by_id(db, product_id)

    if not db_product:
        return None

    db.delete(db_product)
    db.commit()

    return True


# -----------------------------
# Search Products
# -----------------------------
def search_products(db: Session, keyword: str):

    return (
        db.query(Product)
        .filter(
            or_(
                Product.name.ilike(f"%{keyword}%"),
                Product.sku.ilike(f"%{keyword}%")
            )
        )
        .all()
    )


# -----------------------------
# Filter By Category
# -----------------------------
def get_products_by_category(
    db: Session,
    category_id: int
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
    limit: int = 10
):

    return (
        db.query(Product)
        .filter(Product.stock_quantity <= limit)
        .all()
    )


# -----------------------------
# Out Of Stock Products
# -----------------------------
def out_of_stock_products(db: Session):

    return (
        db.query(Product)
        .filter(Product.stock_quantity == 0)
        .all()
    )
