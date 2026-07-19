from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from typing import Optional
from fastapi import Query

from app.config.database import get_db

from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)

from app.services import product_service

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# -----------------------------
# Create Product
# -----------------------------
@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, product)


# -----------------------------
# Get All Products
# -----------------------------
@router.get("/", response_model=list[ProductResponse])
def get_products(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
   return product_service.get_all_products(db, search)

# -----------------------------
# Get Product By ID
# -----------------------------
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# -----------------------------
# Update Product
# -----------------------------
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
):
    updated = product_service.update_product(db, product_id, product)

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    return updated


# -----------------------------
# Delete Product
# -----------------------------
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = product_service.delete_product(db, product_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}


# -----------------------------
# Search Products
# -----------------------------
@router.get("/search/{keyword}", response_model=List[ProductResponse])
def search_products(keyword: str, db: Session = Depends(get_db)):
    return product_service.search_products(db, keyword)


# -----------------------------
# Products By Category
# -----------------------------
@router.get("/category/{category_id}", response_model=List[ProductResponse])
def products_by_category(category_id: int, db: Session = Depends(get_db)):
    return product_service.get_products_by_category(db, category_id)


# -----------------------------
# Low Stock Products
# -----------------------------
@router.get("/low-stock", response_model=List[ProductResponse])
def low_stock(db: Session = Depends(get_db)):
    return product_service.low_stock_products(db)


# -----------------------------
# Out Of Stock Products
# -----------------------------
@router.get("/out-of-stock", response_model=List[ProductResponse])
def out_of_stock(db: Session = Depends(get_db)):
    return product_service.out_of_stock_products(db)