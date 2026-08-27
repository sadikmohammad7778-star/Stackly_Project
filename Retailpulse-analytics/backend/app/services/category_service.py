from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
)
from app.services.audit_service import create_audit_log


def create_category(
    db: Session,
    category: CategoryCreate,
    user_id: int,
    company_id: int,
):
    db_category = Category(
        company_id=company_id,
        name=category.name,
        description=category.description,
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Category",
        action="CREATE",
        description=f"Created category '{db_category.name}'",
    )

    return db_category


def get_all_categories(
    db: Session,
    company_id: int,
):
    return (
        db.query(Category)
        .filter(Category.company_id == company_id)
        .all()
    )


def get_category_by_id(
    db: Session,
    category_id: int,
    company_id: int,
):
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.company_id == company_id,
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    return category


def update_category(
    db: Session,
    category_id: int,
    category: CategoryUpdate,
    user_id: int,
    company_id: int,
):
    db_category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.company_id == company_id,
        )
        .first()
    )

    if not db_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    update_data = category.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        if key != "company_id":
            setattr(db_category, key, value)

    db_category.company_id = company_id

    db.commit()
    db.refresh(db_category)

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Category",
        action="UPDATE",
        description=f"Updated category '{db_category.name}'",
    )

    return db_category


def delete_category(
    db: Session,
    category_id: int,
    user_id: int,
    company_id: int,
):
    db_category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.company_id == company_id,
        )
        .first()
    )

    if not db_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )

    category_name = db_category.name

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