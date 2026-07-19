from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
)


def create_category(db: Session, category: CategoryCreate):

    db_category = Category(
        company_id=category.company_id,
        name=category.name,
        description=category.description,
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


def get_all_categories(db: Session):
    return db.query(Category).all()


def get_category_by_id(db: Session, category_id: int):
    return (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )


def update_category(
    db: Session,
    category_id: int,
    category: CategoryUpdate,
):

    db_category = get_category_by_id(db, category_id)

    if not db_category:
        return None

    update_data = category.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)

    return db_category


def delete_category(db: Session, category_id: int):

    db_category = get_category_by_id(db, category_id)

    if not db_category:
        return None

    db.delete(db_category)
    db.commit()

    return True