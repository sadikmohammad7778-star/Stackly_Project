from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user

from app.models.user import User
from app.models.sale import Sale
from app.models.product import Product

from app.services.export_service import (
    generate_excel,
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

# ==========================================
# Export Sales Report - Excel
# ==========================================

@router.get("/sales/excel")
def export_sales_excel(
    db: Session = Depends(get_db),
):

    sales = db.query(Sale).all()

    data = []

    for sale in sales:
        data.append({
            "Invoice Number": sale.invoice_number,
            "Customer Name": sale.customer_name,
            "Sales Channel": sale.sales_channel,
            "Payment Method": sale.payment_method,
            "Total Amount": sale.total_amount,
            "Created At": sale.created_at.strftime("%d-%m-%Y %H:%M"),
        })

    output = generate_excel(data)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=Sales_Report.xlsx"
        },
    )


# ==========================================
# Export Sales Report - PDF
# ==========================================

@router.get("/sales/pdf")
def export_sales_pdf(
    db: Session = Depends(get_db),
):

    sales = db.query(Sale).all()

    data = []

    for sale in sales:
        data.append({
            "Invoice": sale.invoice_number,
            "Customer": sale.customer_name,
            "Amount": sale.total_amount,
            "Payment": sale.payment_method,
            "Channel": sale.sales_channel,
        })

    output = generate_pdf(
        "Sales Report",
        data,
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=Sales_Report.pdf"
        },
    )


# ==========================================
# Export Inventory Report - Excel
# ==========================================

@router.get("/inventory/excel")
def export_inventory_excel(
    db: Session = Depends(get_db),
):

    products = db.query(Product).all()

    data = []

    for product in products:
        data.append({
            "Product Name": product.name,
            "SKU": product.sku,
            "Brand": product.brand,
            "Unit Price": product.unit_price,
            "Stock Quantity": product.stock_quantity,
            "Status": product.status,
            "Active": "Yes" if product.is_active else "No",
            "Created At": product.created_at.strftime("%d-%m-%Y %H:%M"),
        })

    output = generate_excel(data)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=Inventory_Report.xlsx"
        },
    )


# ==========================================
# Export Inventory Report - PDF
# ==========================================

@router.get("/inventory/pdf")
def export_inventory_pdf(
    db: Session = Depends(get_db),
):

    products = db.query(Product).all()

    data = []

    for product in products:
        data.append({
            "Product": product.name,
            "SKU": product.sku,
            "Price": product.unit_price,
            "Stock": product.stock_quantity,
            "Status": product.status,
        })

    output = generate_pdf(
        "Inventory Report",
        data,
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=Inventory_Report.pdf"
        },
    )


# ==========================================
# Export Demand Forecast - CSV
# ==========================================

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
            "Content-Disposition":
            "attachment; filename=Demand_Forecast_Report.csv"
        },
    )


# ==========================================
# Export Demand Forecast - PDF
# ==========================================

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
            "Content-Disposition":
            "attachment; filename=Demand_Forecast_Report.pdf"
        },
    )