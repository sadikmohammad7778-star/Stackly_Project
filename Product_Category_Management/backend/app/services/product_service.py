from app.services.audit_service import create_audit_log
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.models.category import Category
from app.schemas.product_schema import ProductCreate, ProductUpdate


# Create Product
def create_product(db: Session, product: ProductCreate):

    # Check if category exists
    category = db.query(Category).filter(
        Category.id == product.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    # SKU must be unique within company
    existing_sku = db.query(Product).filter(
        Product.company_id == product.company_id,
        Product.sku == product.sku
    ).first()

    if existing_sku:
        raise HTTPException(
            status_code=400,
            detail="SKU already exists."
        )

    # Product name should be unique within the same category
    existing_product = db.query(Product).filter(
        Product.company_id == product.company_id,
        Product.category_id == product.category_id,
        Product.name == product.name
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="Product already exists in this category."
        )

    # Cost Price Validation
    if product.cost_price > product.unit_price:
        raise HTTPException(
            status_code=400,
            detail="Cost Price cannot exceed Unit Price."
        )

    new_product = Product(
        company_id=product.company_id,
        category_id=product.category_id,
        name=product.name,
        sku=product.sku,
        brand=product.brand,
        description=product.description,
        unit_price=product.unit_price,
        cost_price=product.cost_price,
        stock_quantity=product.stock_quantity,
        unit_of_measure=product.unit_of_measure,
        status=product.status
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    create_audit_log(
    db=db,
    company_id=product.company_id,
    entity_name=product.name,
    action="Product Created",
    performed_by="Admin"
    )

  

    return new_product


# Get All Products
def get_products(db: Session):
    return db.query(Product).all()


# Get Single Product
def get_product(product_id: int, db: Session):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return product


# Update Product
def update_product(product_id: int, product: ProductUpdate, db: Session):

    db_product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    update_data = product.model_dump(exclude_unset=True)

    # Validate Cost Price
    if (
        "cost_price" in update_data
        and "unit_price" in update_data
        and update_data["cost_price"] > update_data["unit_price"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Cost Price cannot exceed Unit Price."
        )

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    create_audit_log(
    db=db,
    company_id=db_product.company_id,
    entity_name=db_product.name,
    action="Product Updated",
    performed_by="Admin"
    )

    return db_product


# Delete Product
def delete_product(product_id: int, db: Session):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )
    
    create_audit_log(
    db=db,
    company_id=product.company_id,
    entity_name=product.name,
    action="Product Deleted",
    performed_by="Admin"
)

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully."}


# Search Product
def search_product(keyword: str, db: Session):

    return db.query(Product).filter(
        or_(
            Product.name.ilike(f"%{keyword}%"),
            Product.sku.ilike(f"%{keyword}%"),
            Product.brand.ilike(f"%{keyword}%")
        )
    ).all()


# Filter Products
def filter_products(
    db: Session,
    category_id: int = None,
    brand: str = None,
    status: str = None
):

    query = db.query(Product)

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if brand:
        query = query.filter(Product.brand == brand)

    if status:
        query = query.filter(Product.status == status)

    return query.all()

# Change Product Status
def change_product_status(product_id: int, status: str, db: Session):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    if status not in ["Active", "Inactive"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be either 'Active' or 'Inactive'."
        )

    product.status = status

    db.commit()
    db.refresh(product)

    create_audit_log(
        db=db,
        company_id=product.company_id,
        entity_name=product.name,
        action=f"Product {status}",
        performed_by="Admin"
    )

    return product

# Sort Products
def sort_products(db: Session, sort_by: str):

    query = db.query(Product)

    if sort_by == "name":
        query = query.order_by(Product.name.asc())

    elif sort_by == "price":
        query = query.order_by(Product.unit_price.asc())

    elif sort_by == "recent":
        query = query.order_by(Product.created_at.desc())

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort option. Use: name, price or recent."
        )

    return query.all()