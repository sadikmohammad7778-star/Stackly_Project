from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.sale import Sale
from app.models.product import Product
from app.services.export_service import generate_excel

router = APIRouter(
    prefix="/export",
    tags=["Export Reports"],
)


from app.services.export_service import (
    generate_excel,
    generate_pdf,
)


# -----------------------------
# Export Sales Report
# -----------------------------
@router.get("/sales/excel")
def export_sales_excel(db: Session = Depends(get_db)):

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
            "Content-Disposition": "attachment; filename=Sales_Report.xlsx"
        },
    )


@router.get("/sales/pdf")
def export_sales_pdf(db: Session = Depends(get_db)):

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
# -----------------------------
# Export Inventory Report
# -----------------------------
@router.get("/inventory/excel")
def export_inventory_excel(db: Session = Depends(get_db)):

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
            "Content-Disposition": "attachment; filename=Inventory_Report.xlsx"
        },
    )



@router.get("/inventory/pdf")
def export_inventory_pdf(db: Session = Depends(get_db)):

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