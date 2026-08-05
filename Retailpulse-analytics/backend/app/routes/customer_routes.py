from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.config.dependency import get_db, get_current_user
from app.models.user import User

from app.schemas.customer_schema import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerProfileResponse,
)

from app.services.customer_service import (
    create_customer,
    get_all_customers,
    get_customer_by_id,
    update_customer,
    delete_customer,
    change_customer_status,
    search_customers,
    filter_customers,
    get_customer_dashboard,
    get_top_customers,
    get_revenue_by_customer_type,
    get_customer_growth,
    get_customer_distribution,
    get_customer_purchase_history,
    get_customer_timeline,
    export_customers_csv,
    export_customers_pdf,
)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)

# =====================================================
# CREATE
# =====================================================

@router.post("/", response_model=CustomerResponse)
def add_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_customer(
            db,
            customer,
            current_user.company_id,
            current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================
# LIST
# =====================================================

@router.get("/", response_model=list[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_customers(
        db,
        current_user.company_id,
    )


# =====================================================
# SEARCH & FILTER (STATIC ROUTES FIRST)
# =====================================================

@router.get("/search/")
def search_customer(
    search: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("SEARCH API HIT")
    
    return search_customers(
        db,
        search,
        current_user.company_id,
    )


@router.get("/filter/")
def filter_customer_data(
    customer_type: str = None,
    status: str = None,
    city: str = None,
    state: str = None,
    country: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return filter_customers(
        db,
        current_user.company_id,
        customer_type,
        status,
        city,
        state,
        country,
    )


# =====================================================
# DASHBOARD & ANALYTICS
# =====================================================

@router.get("/dashboard")
def customer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_customer_dashboard(
        db,
        current_user.company_id,
    )


@router.get("/top-customers")
def top_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_top_customers(
        db,
        current_user.company_id,
    )


@router.get("/revenue-by-type")
def revenue_by_type(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_revenue_by_customer_type(
        db,
        current_user.company_id,
    )


@router.get("/growth")
def growth(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_customer_growth(
        db,
        current_user.company_id,
    )


@router.get("/distribution")
def distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_customer_distribution(
        db,
        current_user.company_id,
    )


# =====================================================
# EXPORT
# =====================================================

@router.get("/export/csv")
def export_customer_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = export_customers_csv(
        db,
        current_user.company_id,
    )

    return FileResponse(
        path=file_path,
        filename="customers.csv",
        media_type="text/csv",
    )


@router.get("/export/pdf")
def export_customer_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = export_customers_pdf(
        db,
        current_user.company_id,
    )

    return FileResponse(
        path=file_path,
        filename="customers.pdf",
        media_type="application/pdf",
    )


# =====================================================
# DYNAMIC ROUTES (KEEP THESE LAST)
# =====================================================

@router.get(
    "/{customer_id}",
    response_model=CustomerProfileResponse,
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_customer_by_id(
            db,
            customer_id,
            current_user.company_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def edit_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_customer(
            db,
            customer_id,
            customer,
            current_user.company_id,
            current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{customer_id}")
def remove_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_customer(
            db,
            customer_id,
            current_user.company_id,
            current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/{customer_id}/status",
    response_model=CustomerResponse,
)
def update_status(
    customer_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return change_customer_status(
            db,
            customer_id,
            status,
            current_user.company_id,
            current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{customer_id}/purchase-history")
def customer_purchase_history(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_customer_purchase_history(
        db,
        customer_id,
        current_user.company_id,
    )


@router.get("/{customer_id}/timeline")
def customer_timeline(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_customer_timeline(
        db,
        customer_id,
        current_user.company_id,
    )