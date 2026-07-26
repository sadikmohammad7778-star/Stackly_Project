from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User

from app.schemas.sale_schema import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SalesSummary,
)

from app.services import sale_service

router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


# -----------------------------
# Create Sale
# -----------------------------
@router.post("/", response_model=SaleResponse)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.create_sale(
        db,
        sale,
        current_user.id,
    )


# -----------------------------
# Get All Sales
# -----------------------------
@router.get("/", response_model=List[SaleResponse])
def get_sales(
    db: Session = Depends(get_db),
):
    return sale_service.get_all_sales(db)


# -----------------------------
# Get Sale By ID
# -----------------------------
@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):
    return sale_service.get_sale_by_id(
        db,
        sale_id,
    )


# -----------------------------
# Update Sale
# -----------------------------
@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    sale: SaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.update_sale(
        db,
        sale_id,
        sale,
        current_user.id,
    )


# -----------------------------
# Delete Sale
# -----------------------------
@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.delete_sale(
        db,
        sale_id,
        current_user.id,
    )


# -----------------------------
# Dashboard Summary
# -----------------------------
@router.get("/summary/dashboard", response_model=SalesSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
):
    return sale_service.sales_summary(db)