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
    ip_address: str = None,
    user_agent: str = None,
):
    db_category = Category(
        company_id=company_id,
        name=category.name,
        description=category.description,
    )

    try:
        db.add(db_category)
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Category",
            action="CREATE",
            resource_type="Category",
            resource_id=str(db_category.id),
            description=f"Created category '{db_category.name}'",
            before_values=None,
            after_values={
                "name": db_category.name,
                "description": db_category.description,
                "company_id": db_category.company_id,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(db_category)

        return db_category

    except Exception:
        db.rollback()
        raise

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
    ip_address: str = None,
    user_agent: str = None,
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

    before_values = {
        "name": db_category.name,
        "description": db_category.description,
        "company_id": db_category.company_id,
    }

    update_data = category.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        if key != "company_id":
            setattr(db_category, key, value)

    db_category.company_id = company_id

    after_values = {
        "name": db_category.name,
        "description": db_category.description,
        "company_id": db_category.company_id,
    }

    try:
        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Category",
            action="UPDATE",
            resource_type="Category",
            resource_id=str(db_category.id),
            description=f"Updated category '{db_category.name}'",
            before_values=before_values,
            after_values=after_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(db_category)

        return db_category

    except Exception:
        db.rollback()
        raise

def delete_category(
    db: Session,
    category_id: int,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
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

    before_values = {
        "name": db_category.name,
        "description": db_category.description,
        "company_id": db_category.company_id,
    }

    category_name = db_category.name
    category_id_value = db_category.id

    try:
        db.delete(db_category)
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Category",
            action="DELETE",
            resource_type="Category",
            resource_id=str(category_id_value),
            description=f"Deleted category '{category_name}'",
            before_values=before_values,
            after_values=None,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()

        return {
            "message": "Category deleted successfully."
        }

    except Exception as e:
        db.rollback()

        if "sale_items_category_id_fkey" in str(e):
            raise HTTPException(
                status_code=409,
                detail="Category cannot be deleted because it is already used in sales.",
            )

        raise