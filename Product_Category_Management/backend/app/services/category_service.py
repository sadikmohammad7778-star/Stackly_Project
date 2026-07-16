from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import func

from app.models.category import Category
from app.models.product import Product
from app.schemas.category_schema import CategoryCreate, CategoryUpdate
from app.services.audit_service import create_audit_log


# Create Category
def create_category(db: Session, category: CategoryCreate):

    existing = db.query(Category).filter(
        func.lower(Category.name) == func.lower(category.name),
        Category.company_id == category.company_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists for this company."
        )

    new_category = Category(
        company_id=category.company_id,
        name=category.name,
        description=category.description,
        status=category.status
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    create_audit_log(
        db=db,
        company_id=new_category.company_id,
        entity_name=new_category.name,
        action="Category Created",
        performed_by="Admin"
    )

    return new_category


# Get All Categories
def get_categories(db: Session):
    return db.query(Category).all()


# Get Category By ID
def get_category(category_id: int, db: Session):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    return category


# Update Category
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session
):

    db_category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not db_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    update_data = category.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)

    create_audit_log(
        db=db,
        company_id=db_category.company_id,
        entity_name=db_category.name,
        action="Category Updated",
        performed_by="Admin"
    )

    return db_category


# Delete Category
def delete_category(category_id: int, db: Session):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    create_audit_log(
        db=db,
        company_id=category.company_id,
        entity_name=category.name,
        action="Category Deleted",
        performed_by="Admin"
    )

    db.delete(category)
    db.commit()

    return {
        "message": "Category deleted successfully."
    }


# Search Categories
def search_category(keyword: str, db: Session):

    return db.query(Category).filter(
        Category.name.ilike(f"%{keyword}%")
    ).all()


# Category Product Count
def get_categories_with_product_count(db: Session):

    results = (
        db.query(
            Category.id,
            Category.company_id,
            Category.name,
            Category.description,
            Category.status,
            func.count(Product.id).label("product_count")
        )
        .outerjoin(
            Product,
            Category.id == Product.category_id
        )
        .group_by(
            Category.id,
            Category.company_id,
            Category.name,
            Category.description,
            Category.status
        )
        .all()
    )

    return [
        {
            "id": row.id,
            "company_id": row.company_id,
            "name": row.name,
            "description": row.description,
            "status": row.status,
            "product_count": row.product_count
        }
        for row in results
    ]