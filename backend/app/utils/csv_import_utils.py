import csv
import io
from typing import Any


# ============================================================
# Configuration
# ============================================================

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
PREVIEW_ROWS = 10


# ============================================================
# Required Columns
# ============================================================

REQUIRED_COLUMNS = {
    "products": {
        "Product Name",
        "SKU",
        "Category",
        "Unit Price",
        "Stock Quantity",
    },
    "customers": {
        "Name",
        "Email",
        "Phone",
    },
    "sales": {
        "Customer",
        "Product",
        "Quantity",
        "Unit Price",
        "Sale Date",
    },
}


# ============================================================
# File Validation
# ============================================================

def validate_csv_file(
    filename: str,
    file_content: bytes,
) -> None:

    if not filename.lower().endswith(".csv"):
        raise ValueError(
            "Only CSV files are supported."
        )

    if not file_content:
        raise ValueError(
            "The uploaded file is empty."
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(
            "File size exceeds the maximum allowed limit of 10 MB."
        )


# ============================================================
# CSV Parsing
# ============================================================

def parse_csv(
    file_content: bytes,
) -> tuple[list[str], list[dict[str, Any]]]:

    try:
        text = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError(
            "CSV file must use UTF-8 encoding."
        )

    try:
        reader = csv.DictReader(
            io.StringIO(text)
        )
    except csv.Error:
        raise ValueError(
            "Unable to read the CSV file."
        )

    if not reader.fieldnames:
        raise ValueError(
            "CSV file does not contain column headers."
        )

    columns = [
        column.strip()
        for column in reader.fieldnames
        if column
    ]

    rows = []

    for row in reader:

        cleaned_row = {}

        for key, value in row.items():

            if key is None:
                continue

            clean_key = key.strip()

            if value is None:
                cleaned_row[clean_key] = ""
            else:
                cleaned_row[clean_key] = value.strip()

        # Ignore completely empty rows
        if any(
            str(value).strip()
            for value in cleaned_row.values()
        ):
            rows.append(cleaned_row)

    return columns, rows


# ============================================================
# Column Validation
# ============================================================

def validate_columns(
    import_type: str,
    columns: list[str],
) -> list[str]:

    import_type = import_type.lower().strip()

    if import_type not in REQUIRED_COLUMNS:
        raise ValueError(
            "Invalid import type. "
            "Supported types: products, customers, sales."
        )

    uploaded_columns = {
        column.strip()
        for column in columns
    }

    required_columns = REQUIRED_COLUMNS[
        import_type
    ]

    missing_columns = sorted(
        required_columns - uploaded_columns
    )

    return missing_columns


# ============================================================
# Preview
# ============================================================

def build_preview(
    rows: list[dict[str, Any]],
    limit: int = PREVIEW_ROWS,
) -> list[dict[str, Any]]:

    return rows[:limit]


# ============================================================
# Complete CSV Inspection
# ============================================================

def inspect_csv(
    import_type: str,
    filename: str,
    file_content: bytes,
) -> dict[str, Any]:

    validate_csv_file(
        filename=filename,
        file_content=file_content,
    )

    columns, rows = parse_csv(
        file_content=file_content,
    )

    missing_columns = validate_columns(
        import_type=import_type,
        columns=columns,
    )

    return {
        "columns": columns,
        "preview": build_preview(rows),
        "total_records": len(rows),
        "missing_columns": missing_columns,
        "valid_columns": not missing_columns,
    }