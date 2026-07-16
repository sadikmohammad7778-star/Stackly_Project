from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)

from app.services.product_service import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product,
    search_product,
    filter_products,
    change_product_status,
    sort_products
)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# Create Product
@router.post("/", response_model=ProductResponse)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, product)


# Get All Products
@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    return get_products(db)


# Search Products
@router.get("/search/{keyword}", response_model=List[ProductResponse])
def search_products(keyword: str, db: Session = Depends(get_db)):
    return search_product(keyword, db)


# Filter Products
@router.get("/filter")
def filter_product(
    category_id: Optional[int] = Query(None),
    brand: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return filter_products(
        db=db,
        category_id=category_id,
        brand=brand,
        status=status
    )


# Change Product Status
@router.patch("/{product_id}/status")
def update_status(
    product_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    return change_product_status(
        product_id,
        status,
        db
    )


@router.get("/sort/{sort_by}")
def sort_product_list(
    sort_by: str,
    db: Session = Depends(get_db)
):
    return sort_products(db, sort_by)


# Get Product By ID
@router.get("/{product_id}", response_model=ProductResponse)
def get_single_product(product_id: int, db: Session = Depends(get_db)):
    return get_product(product_id, db)


# Update Product
@router.put("/{product_id}", response_model=ProductResponse)
def edit_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    return update_product(product_id, product, db)


# Delete Product
@router.delete("/{product_id}")
def remove_product(product_id: int, db: Session = Depends(get_db)):
    return delete_product(product_id, db)