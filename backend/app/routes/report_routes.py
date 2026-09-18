import os
from datetime import date

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User
from app.models.report_history import ReportHistory

from app.schemas.report_schema import (
    ReportFilters,
    SalesReport,
    StockReport,
    SalesReportResponse,
    InventoryReportResponse,
    CustomerReportResponse,
    ProductPerformanceResponse,
    StockMovementReportResponse,
    ReportHistoryResponse,
    ReportHistoryListResponse,
)

from app.services.report_service import (
    get_sales_report,
    get_stock_report,
    get_sales_report_data,
    get_inventory_report_data,
    get_customer_report_data,
    get_product_performance_report_data,
    get_stock_movement_report_data,
    get_report_history,
    get_report_history_by_id,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/sales/summary",
    response_model=SalesReport,
)
def sales_report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_sales_report(
        db=db,
        company_id=current_user.company_id,
    )


@router.get(
    "/stock/summary",
    response_model=StockReport,
)
def stock_report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_stock_report(
        db=db,
        company_id=current_user.company_id,
    )


@router.get(
    "/sales",
    response_model=SalesReportResponse,
)
def sales_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    customer_id: int | None = Query(None),
    sales_status: str | None = Query(None),
    stock_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        product_id=product_id,
        category_id=category_id,
        brand=brand,
        customer_id=customer_id,
        sales_status=sales_status,
        stock_status=stock_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    return get_sales_report_data(
        db=db,
        company_id=current_user.company_id,
        filters=filters,
    )


@router.get(
    "/inventory",
    response_model=InventoryReportResponse,
)
def inventory_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    customer_id: int | None = Query(None),
    sales_status: str | None = Query(None),
    stock_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        product_id=product_id,
        category_id=category_id,
        brand=brand,
        customer_id=customer_id,
        sales_status=sales_status,
        stock_status=stock_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    return get_inventory_report_data(
        db=db,
        company_id=current_user.company_id,
        filters=filters,
    )


@router.get(
    "/customers",
    response_model=CustomerReportResponse,
)
def customer_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    customer_id: int | None = Query(None),
    sales_status: str | None = Query(None),
    stock_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        product_id=product_id,
        category_id=category_id,
        brand=brand,
        customer_id=customer_id,
        sales_status=sales_status,
        stock_status=stock_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    return get_customer_report_data(
        db=db,
        company_id=current_user.company_id,
        filters=filters,
    )


@router.get(
    "/products",
    response_model=ProductPerformanceResponse,
)
def product_performance_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    customer_id: int | None = Query(None),
    sales_status: str | None = Query(None),
    stock_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        product_id=product_id,
        category_id=category_id,
        brand=brand,
        customer_id=customer_id,
        sales_status=sales_status,
        stock_status=stock_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    return get_product_performance_report_data(
        db=db,
        company_id=current_user.company_id,
        filters=filters,
    )


@router.get(
    "/stock-movements",
    response_model=StockMovementReportResponse,
)
def stock_movement_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    customer_id: int | None = Query(None),
    sales_status: str | None = Query(None),
    stock_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        product_id=product_id,
        category_id=category_id,
        brand=brand,
        customer_id=customer_id,
        sales_status=sales_status,
        stock_status=stock_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    return get_stock_movement_report_data(
        db=db,
        company_id=current_user.company_id,
        filters=filters,
    )


@router.get(
    "/history",
    response_model=ReportHistoryListResponse,
)
def report_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_report_history(
        db=db,
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/history/{history_id}/download",
)
def download_report_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = (
        db.query(ReportHistory)
        .filter(
            ReportHistory.id == history_id,
            ReportHistory.company_id == current_user.company_id,
        )
        .first()
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Report history not found",
        )

    if not history.file_path:
        raise HTTPException(
            status_code=404,
            detail="Report file is not available",
        )

    base_directory = os.path.abspath("generated_reports")
    file_path = os.path.abspath(history.file_path)

    try:
        common_path = os.path.commonpath(
            [base_directory, file_path]
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid report file path",
        )

    if common_path != base_directory:
        raise HTTPException(
            status_code=400,
            detail="Invalid report file path",
        )

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail="Report file not found on server",
        )

    if history.format.upper() == "PDF":
        media_type = "application/pdf"
    elif history.format.upper() == "CSV":
        media_type = "text/csv"
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type=media_type,
    )


@router.get(
    "/history/{history_id}",
    response_model=ReportHistoryResponse,
)
def report_history_detail(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = get_report_history_by_id(
        db=db,
        company_id=current_user.company_id,
        history_id=history_id,
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Report history not found",
        )

    return history