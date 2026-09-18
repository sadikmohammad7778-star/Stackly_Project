from io import BytesIO, StringIO
import csv
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph


REPORT_DIRECTORY = "generated_reports"


def ensure_report_directory():
    os.makedirs(REPORT_DIRECTORY, exist_ok=True)


def generate_csv(data, file_path=None):
    output = StringIO()

    if not data:
        output.write("No Data Available\n")
    else:
        fieldnames = list(data[0].keys())

        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(data)

    csv_content = output.getvalue()

    if file_path:
        ensure_report_directory()

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            file.write(csv_content)

    return csv_content


def generate_pdf(
    title,
    data,
    filters=None,
    file_path=None
):
    output = BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4)
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph(
            title,
            styles["Heading1"]
        )
    ]

    if filters:
        filter_text = "Applied Filters: "

        filter_text += ", ".join(
            f"{key}: {value}"
            for key, value in filters.items()
            if value is not None
        )

        elements.append(
            Paragraph(
                filter_text,
                styles["Normal"]
            )
        )

    if not data:
        elements.append(
            Paragraph(
                "No Data Available",
                styles["Normal"]
            )
        )

        doc.build(elements)

        pdf_content = output.getvalue()

        if file_path:
            ensure_report_directory()

            with open(
                file_path,
                "wb"
            ) as file:
                file.write(pdf_content)

        return pdf_content

    headers = list(data[0].keys())

    rows = [headers]

    for item in data:
        rows.append(
            [
                str(item.get(header, ""))
                for header in headers
            ]
        )

    table = Table(
        rows,
        repeatRows=1
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f4e78")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    elements.append(table)

    doc.build(elements)

    pdf_content = output.getvalue()

    if file_path:
        ensure_report_directory()

        with open(
            file_path,
            "wb"
        ) as file:
            file.write(pdf_content)

    return pdf_content