from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config.dependency import (
    get_db,
    get_current_user,
)

from app.models.user import User

from app.schemas.sale_schema import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SalesSummary,
)

from app.services import sale_service
from app.services.invoice_service import (
    generate_invoice_pdf,
    generate_invoice_csv,
)

# ============================================================
# Sales Router
# ============================================================

router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


# ============================================================
# Create Sale
# ============================================================

@router.post(
    "/",
    response_model=SaleResponse,
)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.create_sale(
        db=db,
        sale=sale,
        user_id=current_user.id,
        company_id=current_user.company_id,
    )

# ============================================================
# Sales Dashboard Summary
# ============================================================

@router.get(
    "/summary/dashboard",
    response_model=SalesSummary,
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.sales_summary(
        db=db,
        company_id=current_user.company_id,
    )


# ============================================================
# Search Sales
# ============================================================

@router.get(
    "/search",
    response_model=List[SaleResponse],
)
def search_sales(
    keyword: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    payment_method: str | None = None,
    status: str | None = None,
    sort: str = "date",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.search_sales(
        db=db,
        keyword=keyword,
        company_id=current_user.company_id,
        start_date=start_date,
        end_date=end_date,
        payment_method=payment_method,
        status=status,
        sort=sort,
        order=order,
    )


# ============================================================
# Get All Sales
# ============================================================

@router.get(
    "/",
    response_model=List[SaleResponse],
)
def get_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_all_sales(
        db=db,
        company_id=current_user.company_id,
    )


# ============================================================
# Generate Invoice PDF
# ============================================================

@router.get(
    "/{sale_id}/invoice/pdf",
)
def download_invoice_pdf(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pdf = generate_invoice_pdf(
        db=db,
        sale_id=sale_id,
        company_id=current_user.company_id,
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"attachment; "
                f"filename=invoice-{sale_id}.pdf"
            )
        },
    )

# ============================================================
# Generate Invoice CSV
# ============================================================

@router.get(
    "/{sale_id}/invoice/csv",
)
def download_invoice_csv(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    csv_file = generate_invoice_csv(
        db=db,
        sale_id=sale_id,
        company_id=current_user.company_id,
    )

    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f"attachment; "
                f"filename=invoice-{sale_id}.csv"
            )
        },
    )

# ============================================================
# Get Sale By ID
# ============================================================

@router.get(
    "/{sale_id}",
    response_model=SaleResponse,
)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_sale_by_id(
        db=db,
        sale_id=sale_id,
        company_id=current_user.company_id,
    )


# ============================================================
# Update Sale
# ============================================================

@router.put(
    "/{sale_id}",
    response_model=SaleResponse,
)
def update_sale(
    sale_id: int,
    sale: SaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.update_sale(
        db=db,
        sale_id=sale_id,
        sale=sale,
        user_id=current_user.id,
        company_id=current_user.company_id,
    )

# ============================================================
# Delete Sale
# ============================================================

@router.delete(
    "/{sale_id}",
)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.delete_sale(
        db=db,
        sale_id=sale_id,
        user_id=current_user.id,
        company_id=current_user.company_id,
    )