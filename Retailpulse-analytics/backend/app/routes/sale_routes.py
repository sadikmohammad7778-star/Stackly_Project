from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db

from app.schemas.sale_schema import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SalesSummary,
)

from app.services import sale_service

router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)


# -----------------------------
# Create Sale
# -----------------------------
@router.post("/", response_model=SaleResponse)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
):
    return sale_service.create_sale(db, sale)


# -----------------------------
# Get All Sales
# -----------------------------
@router.get("/", response_model=List[SaleResponse])
def get_sales(db: Session = Depends(get_db)):
    return sale_service.get_all_sales(db)


# -----------------------------
# Get Sale By ID
# -----------------------------
@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):
    sale = sale_service.get_sale_by_id(db, sale_id)

    if not sale:
        raise HTTPException(
            status_code=404,
            detail="Sale not found",
        )

    return sale


# -----------------------------
# Update Sale
# -----------------------------
@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    sale: SaleUpdate,
    db: Session = Depends(get_db),
):
    updated = sale_service.update_sale(
        db,
        sale_id,
        sale,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Sale not found",
        )

    return updated


# -----------------------------
# Delete Sale
# -----------------------------
@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):
    deleted = sale_service.delete_sale(db, sale_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Sale not found",
        )

    return {
        "message": "Sale deleted successfully"
    }


# -----------------------------
# Dashboard Summary
# -----------------------------
@router.get("/summary/dashboard", response_model=SalesSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
):
    return sale_service.sales_summary(db)