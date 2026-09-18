from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User

from app.schemas.report_schema import ReportFilters

from app.services.report_service import (
    get_sales_report_data,
    get_inventory_report_data,
    get_customer_report_data,
    get_product_performance_report_data,
    get_stock_movement_report_data,
)

from app.services.export_service import (
    generate_csv,
    generate_pdf,
)

from app.services.demand_forecast_service import (
    export_forecast_csv,
    export_forecast_pdf,
)


router = APIRouter(
    prefix="/export",
    tags=["Export Reports"],
)


def get_all_report_data(
    report_function,
    db,
    company_id,
    filters,
):
    all_data = []
    page = 1

    while True:
        page_filters = filters.model_copy(
            update={
                "page": page,
                "page_size": 100,
            }
        )

        result = report_function(
            db=db,
            company_id=company_id,
            filters=page_filters,
        )

        all_data.extend(
            [
                item.model_dump()
                for item in result.data
            ]
        )

        if page >= result.total_pages:
            break

        page += 1

    return all_data


def build_filters(
    start_date,
    end_date,
    product_id,
    category_id,
    brand,
    customer_id,
    sales_status,
    stock_status,
    sort_by,
    sort_order,
):
    return ReportFilters(
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
        page=1,
        page_size=100,
    )


def filter_context(filters):
    return {
        "Start Date": str(filters.start_date)
        if filters.start_date
        else None,
        "End Date": str(filters.end_date)
        if filters.end_date
        else None,
        "Product ID": filters.product_id,
        "Category ID": filters.category_id,
        "Brand": filters.brand,
        "Customer ID": filters.customer_id,
        "Sales Status": filters.sales_status,
        "Stock Status": filters.stock_status,
    }


@router.get("/sales/csv")
def export_sales_csv(
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        product_id,
        category_id,
        brand,
        customer_id,
        sales_status,
        stock_status,
        sort_by,
        sort_order,
    )

    data = get_all_report_data(
        get_sales_report_data,
        db,
        current_user.company_id,
        filters,
    )

    csv_data = generate_csv(data)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Sales_Report.csv"
            )
        },
    )


@router.get("/sales/pdf")
def export_sales_pdf(
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        product_id,
        category_id,
        brand,
        customer_id,
        sales_status,
        stock_status,
        sort_by,
        sort_order,
    )

    data = get_all_report_data(
        get_sales_report_data,
        db,
        current_user.company_id,
        filters,
    )

    pdf_data = generate_pdf(
        "Sales Report",
        data,
        filter_context(filters),
    )

    return Response(
        content=pdf_data.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Sales_Report.pdf"
            )
        },
    )


@router.get("/inventory/csv")
def export_inventory_csv(
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        product_id,
        category_id,
        brand,
        customer_id,
        sales_status,
        stock_status,
        sort_by,
        sort_order,
    )

    data = get_all_report_data(
        get_inventory_report_data,
        db,
        current_user.company_id,
        filters,
    )

    csv_data = generate_csv(data)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Inventory_Report.csv"
            )
        },
    )


@router.get("/inventory/pdf")
def export_inventory_pdf(
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        product_id,
        category_id,
        brand,
        customer_id,
        sales_status,
        stock_status,
        sort_by,
        sort_order,
    )

    data = get_all_report_data(
        get_inventory_report_data,
        db,
        current_user.company_id,
        filters,
    )

    pdf_data = generate_pdf(
        "Inventory Report",
        data,
        filter_context(filters),
    )

    return Response(
        content=pdf_data.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Inventory_Report.pdf"
            )
        },
    )


@router.get("/customers/csv")
def export_customers_csv(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    customer_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        None,
        None,
        None,
        customer_id,
        None,
        None,
        None,
        "desc",
    )

    data = get_all_report_data(
        get_customer_report_data,
        db,
        current_user.company_id,
        filters,
    )

    csv_data = generate_csv(data)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Customer_Report.csv"
            )
        },
    )


@router.get("/customers/pdf")
def export_customers_pdf(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    customer_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        None,
        None,
        None,
        customer_id,
        None,
        None,
        None,
        "desc",
    )

    data = get_all_report_data(
        get_customer_report_data,
        db,
        current_user.company_id,
        filters,
    )

    pdf_data = generate_pdf(
        "Customer Report",
        data,
        filter_context(filters),
    )

    return Response(
        content=pdf_data.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Customer_Report.pdf"
            )
        },
    )


@router.get("/products/csv")
def export_products_csv(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    customer_id: int | None = Query(None),
    sales_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        product_id,
        category_id,
        brand,
        customer_id,
        sales_status,
        None,
        sort_by,
        sort_order,
    )

    data = get_all_report_data(
        get_product_performance_report_data,
        db,
        current_user.company_id,
        filters,
    )

    csv_data = generate_csv(data)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Product_Performance_Report.csv"
            )
        },
    )


@router.get("/products/pdf")
def export_products_pdf(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    customer_id: int | None = Query(None),
    sales_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        product_id,
        category_id,
        brand,
        customer_id,
        sales_status,
        None,
        sort_by,
        sort_order,
    )

    data = get_all_report_data(
        get_product_performance_report_data,
        db,
        current_user.company_id,
        filters,
    )

    pdf_data = generate_pdf(
        "Product Performance Report",
        data,
        filter_context(filters),
    )

    return Response(
        content=pdf_data.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Product_Performance_Report.pdf"
            )
        },
    )


@router.get("/stock-movements/csv")
def export_stock_movements_csv(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    stock_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        product_id,
        category_id,
        brand,
        None,
        None,
        stock_status,
        sort_by,
        sort_order,
    )

    data = get_all_report_data(
        get_stock_movement_report_data,
        db,
        current_user.company_id,
        filters,
    )

    csv_data = generate_csv(data)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Stock_Movement_Report.csv"
            )
        },
    )


@router.get("/stock-movements/pdf")
def export_stock_movements_pdf(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    product_id: int | None = Query(None),
    category_id: int | None = Query(None),
    brand: str | None = Query(None),
    stock_status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = build_filters(
        start_date,
        end_date,
        product_id,
        category_id,
        brand,
        None,
        None,
        stock_status,
        sort_by,
        sort_order,
    )

    data = get_all_report_data(
        get_stock_movement_report_data,
        db,
        current_user.company_id,
        filters,
    )

    pdf_data = generate_pdf(
        "Stock Movement Report",
        data,
        filter_context(filters),
    )

    return Response(
        content=pdf_data.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Stock_Movement_Report.pdf"
            )
        },
    )


@router.get("/forecast/csv")
def export_forecast_csv_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    csv_data = export_forecast_csv(
        db=db,
        company_id=current_user.company_id,
    )

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Demand_Forecast_Report.csv"
            )
        },
    )


@router.get("/forecast/pdf")
def export_forecast_pdf_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pdf_data = export_forecast_pdf(
        db=db,
        company_id=current_user.company_id,
    )

    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=Demand_Forecast_Report.pdf"
            )
        },
    )