from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.config.database import get_db
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from app.services.category_service import (
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category,
    search_category,
    get_categories_with_product_count
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post("/", response_model=CategoryResponse)
def add_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, category)


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    return get_categories(db)


# Product Count
@router.get("/product-count")
def category_product_count(db: Session = Depends(get_db)):
    return get_categories_with_product_count(db)


# Search Category
@router.get("/search/{keyword}", response_model=List[CategoryResponse])
def search_categories(keyword: str, db: Session = Depends(get_db)):
    return search_category(keyword, db)


# Get Category by ID
@router.get("/{category_id}", response_model=CategoryResponse)
def get_single_category(category_id: int, db: Session = Depends(get_db)):
    return get_category(category_id, db)


# Update Category
@router.put("/{category_id}", response_model=CategoryResponse)
def edit_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    return update_category(category_id, category, db)


# Delete Category
@router.delete("/{category_id}")
def remove_category(category_id: int, db: Session = Depends(get_db)):
    return delete_category(category_id, db)