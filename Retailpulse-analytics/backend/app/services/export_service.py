from io import BytesIO
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
)


# -----------------------------
# Excel Export
# -----------------------------
def generate_excel(data):
    df = pd.DataFrame(data)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)

    return output


# -----------------------------
# PDF Export
# -----------------------------
def generate_pdf(title, data):

    output = BytesIO()

    doc = SimpleDocTemplate(output)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph(title, styles["Heading1"]))

    if not data:
        elements.append(
            Paragraph("No Data Available", styles["Normal"])
        )
    else:

        headers = list(data[0].keys())

        rows = [headers]

        for item in data:
            rows.append([str(item[h]) for h in headers])

        table = Table(rows)

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )

        elements.append(table)

    doc.build(elements)

    output.seek(0)

    return output