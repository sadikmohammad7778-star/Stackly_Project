from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
)
from app.services.audit_service import create_audit_log


# -----------------------------------
# Create Category
# -----------------------------------
def create_category(
    db: Session,
    category: CategoryCreate,
    user_id: int,
):
    db_category = Category(
        company_id=category.company_id,
        name=category.name,
        description=category.description,
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    create_audit_log(
        db=db,
        company_id=db_category.company_id,
        user_id=user_id,
        module="Category",
        action="CREATE",
        description=f"Created category '{db_category.name}'",
    )

    return db_category


# -----------------------------------
# Get All Categories
# -----------------------------------
def get_all_categories(db: Session):
    return db.query(Category).all()


# -----------------------------------
# Get Category By ID
# -----------------------------------
def get_category_by_id(
    db: Session,
    category_id: int,
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    return category


# -----------------------------------
# Update Category
# -----------------------------------
def update_category(
    db: Session,
    category_id: int,
    category: CategoryUpdate,
    user_id: int,
):
    db_category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

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
        user_id=user_id,
        module="Category",
        action="UPDATE",
        description=f"Updated category '{db_category.name}'",
    )

    return db_category


# -----------------------------------
# Delete Category
# -----------------------------------
def delete_category(
    db: Session,
    category_id: int,
    user_id: int,
):
    db_category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not db_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    category_name = db_category.name
    company_id = db_category.company_id

    db.delete(db_category)
    db.commit()

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Category",
        action="DELETE",
        description=f"Deleted category '{category_name}'",
    )

    return {
        "message": "Category deleted successfully."
    }