from io import BytesIO, StringIO
import csv
import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.models.sale import Sale


# ============================================================
# Font Setup
# ============================================================

def register_invoice_fonts():
    """
    Register Segoe UI fonts.
    Segoe UI supports the Indian Rupee symbol (₹).
    """

    font_regular = "SegoeUI"
    font_bold = "SegoeUI-Bold"

    regular_path = r"C:\Windows\Fonts\segoeui.ttf"
    bold_path = r"C:\Windows\Fonts\segoeuib.ttf"

    if not os.path.exists(regular_path):
        raise FileNotFoundError(
            f"Font not found: {regular_path}"
        )

    if not os.path.exists(bold_path):
        raise FileNotFoundError(
            f"Font not found: {bold_path}"
        )

    pdfmetrics.registerFont(
        TTFont(
            font_regular,
            regular_path,
        )
    )

    pdfmetrics.registerFont(
        TTFont(
            font_bold,
            bold_path,
        )
    )

    return font_regular, font_bold

# ============================================================
# Currency Helper
# ============================================================

def format_currency(value):
    """
    Format amount using Indian currency format.
    """

    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0

    return f"₹{value:,.2f}"


# ============================================================
# Generate Invoice PDF
# ============================================================

def generate_invoice_pdf(
    db: Session,
    sale_id: int,
    company_id: int,
):

    # --------------------------------------------------------
    # Get Sale
    # --------------------------------------------------------

    sale = (
        db.query(Sale)
        .filter(
            Sale.id == sale_id,
            Sale.company_id == company_id,
        )
        .first()
    )

    if sale is None:

        raise HTTPException(
            status_code=404,
            detail="Sale not found.",
        )

    # --------------------------------------------------------
    # Register Fonts
    # --------------------------------------------------------

    regular_font, bold_font = register_invoice_fonts()

    # --------------------------------------------------------
    # PDF Buffer
    # --------------------------------------------------------

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    # --------------------------------------------------------
    # Styles
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
        spaceAfter=8,
    )

    heading_style = ParagraphStyle(
        "InvoiceHeading",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#111827"),
        spaceAfter=10,
    )

    normal_style = ParagraphStyle(
        "InvoiceNormal",
        parent=styles["Normal"],
        fontName=regular_font,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
    )

    bold_style = ParagraphStyle(
        "InvoiceBold",
        parent=normal_style,
        fontName=bold_font,
    )

    right_style = ParagraphStyle(
        "InvoiceRight",
        parent=normal_style,
        alignment=TA_RIGHT,
    )

    right_bold_style = ParagraphStyle(
        "InvoiceRightBold",
        parent=right_style,
        fontName=bold_font,
    )

    elements = []

    # ========================================================
    # Header
    # ========================================================

    elements.append(
        Paragraph(
            "RETAILPULSE",
            title_style,
        )
    )

    elements.append(
        Paragraph(
            "SALES INVOICE",
            heading_style,
        )
    )

    elements.append(
        Spacer(1, 8)
    )

    # ========================================================
    # Invoice Information
    # ========================================================

    sale_date = ""

    if sale.sale_date:
        sale_date = sale.sale_date.strftime(
            "%d-%m-%Y %H:%M"
        )

    invoice_info = [

        [
            Paragraph(
                "Invoice Number",
                bold_style,
            ),
            Paragraph(
                str(sale.invoice_number or ""),
                normal_style,
            ),
        ],

        [
            Paragraph(
                "Sale Date",
                bold_style,
            ),
            Paragraph(
                sale_date,
                normal_style,
            ),
        ],

        [
            Paragraph(
                "Customer",
                bold_style,
            ),
            Paragraph(
                str(sale.customer_name or ""),
                normal_style,
            ),
        ],

        [
            Paragraph(
                "Payment Method",
                bold_style,
            ),
            Paragraph(
                str(sale.payment_method or ""),
                normal_style,
            ),
        ],

        [
            Paragraph(
                "Sales Channel",
                bold_style,
            ),
            Paragraph(
                str(sale.sales_channel or ""),
                normal_style,
            ),
        ],

        [
            Paragraph(
                "Status",
                bold_style,
            ),
            Paragraph(
                str(sale.status or ""),
                normal_style,
            ),
        ],
    ]

    info_table = Table(
        invoice_info,
        colWidths=[
            45 * mm,
            115 * mm,
        ],
    )

    info_table.setStyle(
        TableStyle(
            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#9CA3AF"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F3F4F6"),
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(info_table)

    elements.append(
        Spacer(1, 15)
    )

    # ========================================================
    # Product Table
    # ========================================================

    product_data = [

        [
            Paragraph("Product", bold_style),
            Paragraph("SKU", bold_style),
            Paragraph("Qty", bold_style),
            Paragraph("Unit Price", bold_style),
            Paragraph("Discount", bold_style),
            Paragraph("Tax", bold_style),
            Paragraph("Total", bold_style),
        ]

    ]

    subtotal = 0

    for item in sale.items:

        product_name = (
            item.product.name
            if item.product
            else "Unknown Product"
        )

        sku = (
            item.product.sku
            if item.product
            else "N/A"
        )

        quantity = int(
            item.quantity or 0
        )

        unit_price = float(
            item.unit_price or 0
        )

        discount = float(
            item.discount or 0
        )

        tax = float(
            item.tax or 0
        )

        total = float(
            item.total or 0
        )

        line_subtotal = (
            quantity * unit_price
        )

        subtotal += line_subtotal

        product_data.append(

            [
                Paragraph(
                    str(product_name),
                    normal_style,
                ),

                Paragraph(
                    str(sku),
                    normal_style,
                ),

                Paragraph(
                    str(quantity),
                    right_style,
                ),

                Paragraph(
                    format_currency(unit_price),
                    right_style,
                ),

                Paragraph(
                    format_currency(discount),
                    right_style,
                ),

                Paragraph(
                    format_currency(tax),
                    right_style,
                ),

                Paragraph(
                    format_currency(total),
                    right_bold_style,
                ),
            ]
        )

    product_table = Table(
        product_data,
        repeatRows=1,
        colWidths=[
            35 * mm,
            20 * mm,
            12 * mm,
            27 * mm,
            22 * mm,
            18 * mm,
            27 * mm,
        ],
    )

    product_table.setStyle(
        TableStyle(
            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E5E7EB"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#111827"),
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#9CA3AF"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(
        product_table
    )

    elements.append(
        Spacer(1, 15)
    )

    # ========================================================
    # Pricing Summary
    # ========================================================

    sale_discount = float(
        sale.discount or 0
    )

    sale_tax = float(
        sale.tax or 0
    )

    total_amount = float(
        sale.total_amount or 0
    )

    summary_data = [

        [
            Paragraph(
                "Subtotal",
                normal_style,
            ),
            Paragraph(
                format_currency(subtotal),
                right_style,
            ),
        ],

        [
            Paragraph(
                "Discount",
                normal_style,
            ),
            Paragraph(
                format_currency(sale_discount),
                right_style,
            ),
        ],

        [
            Paragraph(
                "Tax",
                normal_style,
            ),
            Paragraph(
                format_currency(sale_tax),
                right_style,
            ),
        ],

        [
            Paragraph(
                "Grand Total",
                bold_style,
            ),
            Paragraph(
                format_currency(total_amount),
                right_bold_style,
            ),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            50 * mm,
            45 * mm,
        ],
        hAlign="RIGHT",
    )

    summary_table.setStyle(
        TableStyle(
            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#9CA3AF"),
                ),

                (
                    "BACKGROUND",
                    (0, 3),
                    (-1, 3),
                    colors.HexColor("#F3F4F6"),
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(
        summary_table
    )

    elements.append(
        Spacer(1, 20)
    )

    # ========================================================
    # Footer
    # ========================================================

    elements.append(
        Paragraph(
            "Thank you for your business.",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            "Generated by RetailPulse",
            normal_style,
        )
    )

    # ========================================================
    # Build PDF
    # ========================================================

    document.build(
        elements
    )

    buffer.seek(0)

    return buffer


# ============================================================
# Generate Invoice CSV
# ============================================================

def generate_invoice_csv(
    db: Session,
    sale_id: int,
    company_id: int,
):

    # --------------------------------------------------------
    # Get Sale
    # --------------------------------------------------------

    sale = (
        db.query(Sale)
        .filter(
            Sale.id == sale_id,
            Sale.company_id == company_id,
        )
        .first()
    )

    if sale is None:

        raise HTTPException(
            status_code=404,
            detail="Sale not found.",
        )

    # --------------------------------------------------------
    # CSV Buffer
    # --------------------------------------------------------

    output = StringIO()

    writer = csv.writer(
        output
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    writer.writerow(
        ["RETAILPULSE"]
    )

    writer.writerow(
        ["SALES INVOICE"]
    )

    writer.writerow([])

    # --------------------------------------------------------
    # Invoice Information
    # --------------------------------------------------------

    writer.writerow(
        [
            "Invoice Number",
            sale.invoice_number,
        ]
    )

    writer.writerow(
        [
            "Sale Date",
            sale.sale_date.strftime(
                "%d-%m-%Y %H:%M"
            )
            if sale.sale_date
            else "",
        ]
    )

    writer.writerow(
        [
            "Customer",
            sale.customer_name,
        ]
    )

    writer.writerow(
        [
            "Payment Method",
            sale.payment_method,
        ]
    )

    writer.writerow(
        [
            "Sales Channel",
            sale.sales_channel,
        ]
    )

    writer.writerow(
        [
            "Status",
            sale.status,
        ]
    )

    writer.writerow([])

    # --------------------------------------------------------
    # Product Headers
    # --------------------------------------------------------

    writer.writerow(
        [
            "Product",
            "SKU",
            "Quantity",
            "Unit Price",
            "Discount",
            "Tax",
            "Line Total",
        ]
    )

    subtotal = 0

    # --------------------------------------------------------
    # Sale Items
    # --------------------------------------------------------

    for item in sale.items:

        product_name = (
            item.product.name
            if item.product
            else "Unknown Product"
        )

        sku = (
            item.product.sku
            if item.product
            else "N/A"
        )

        quantity = int(
            item.quantity or 0
        )

        unit_price = float(
            item.unit_price or 0
        )

        discount = float(
            item.discount or 0
        )

        tax = float(
            item.tax or 0
        )

        total = float(
            item.total or 0
        )

        line_subtotal = (
            quantity * unit_price
        )

        subtotal += line_subtotal

        writer.writerow(
            [
                product_name,
                sku,
                quantity,
                f"{unit_price:.2f}",
                f"{discount:.2f}",
                f"{tax:.2f}",
                f"{total:.2f}",
            ]
        )

    # --------------------------------------------------------
    # Pricing Summary
    # --------------------------------------------------------

    writer.writerow([])

    writer.writerow(
        [
            "Subtotal",
            f"{subtotal:.2f}",
        ]
    )

    writer.writerow(
        [
            "Discount",
            f"{float(sale.discount or 0):.2f}",
        ]
    )

    writer.writerow(
        [
            "Tax",
            f"{float(sale.tax or 0):.2f}",
        ]
    )

    writer.writerow(
        [
            "Grand Total",
            f"{float(sale.total_amount or 0):.2f}",
        ]
    )

    output.seek(0)

    return output