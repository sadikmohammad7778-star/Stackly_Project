from __future__ import annotations

import os
import re
from datetime import datetime
from io import BytesIO, StringIO
from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.customer import Customer
from app.models.customer_purchase_summary import CustomerPurchaseSummary
from app.models.customer_timeline import CustomerTimeline
from app.models.import_error import ImportError
from app.models.import_history import ImportHistory
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem

from app.services.notification_service import NotificationService


# ============================================================
# Constants
# ============================================================

SUPPORTED_IMPORT_TYPES = {
    "products",
    "customers",
    "sales",
}

PRODUCT_REQUIRED_COLUMNS = {
    "sku",
    "name",
    "category",
    "brand",
    "price",
    "stock",
}

CUSTOMER_REQUIRED_COLUMNS = {
    "name",
    "email",
    "phone",
}

SALES_REQUIRED_COLUMNS = {
    "invoice_number",
    "customer_email",
    "sku",
    "quantity",
    "sales_channel",
    "payment_method",
}


# ============================================================
# General Helpers
# ============================================================

def normalize_column_name(column: Any) -> str:
    value = str(column).strip().lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value,
    )

    value = re.sub(
        r"_+",
        "_",
        value,
    )

    return value.strip("_")


def normalize_text(value: Any) -> str:

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value).strip()


def normalize_email(value: Any) -> str:
    return normalize_text(value).lower()


def normalize_phone(value: Any) -> str:
    value = normalize_text(value)

    return re.sub(
        r"\D",
        "",
        value,
    )


def parse_float(value: Any) -> float | None:

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    try:
        return float(value)

    except (ValueError, TypeError):
        return None


def parse_int(value: Any) -> int | None:

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    try:

        number = float(value)

        if not number.is_integer():
            return None

        return int(number)

    except (ValueError, TypeError):
        return None


def validate_email(email: str) -> bool:

    return bool(
        re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            email,
        )
    )


def split_customer_name(
    name: str,
) -> tuple[str, str]:

    parts = normalize_text(name).split()

    if not parts:
        return "", ""

    if len(parts) == 1:
        return parts[0], "Customer"

    return (
        parts[0],
        " ".join(parts[1:]),
    )


def calculate_stock_status(
    available_stock: int,
    reorder_level: int = 10,
) -> str:

    if available_stock <= 0:
        return "Out of Stock"

    if available_stock <= reorder_level:
        return "Low Stock"

    return "In Stock"


# ============================================================
# File Handling
# ============================================================

def read_import_file(
    file_bytes: bytes,
    filename: str,
) -> pd.DataFrame:

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only CSV files are supported.",
        )

    try:
        df = pd.read_csv(
            BytesIO(file_bytes)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read CSV file: {exc}",
        )

    if df.empty:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file contains no records.",
        )

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    df = (
        df
        .dropna(how="all")
        .reset_index(drop=True)
    )

    if df.empty:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file contains no valid records.",
        )

    return df


# ============================================================
# Import Type
# ============================================================

def validate_import_type(
    import_type: str,
) -> str:

    import_type = normalize_text(
        import_type
    ).lower()

    if import_type not in SUPPORTED_IMPORT_TYPES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid import type. "
                "Use products, customers, or sales."
            ),
        )

    return import_type


def get_required_columns(
    import_type: str,
) -> set[str]:

    if import_type == "products":
        return PRODUCT_REQUIRED_COLUMNS

    if import_type == "customers":
        return CUSTOMER_REQUIRED_COLUMNS

    if import_type == "sales":
        return SALES_REQUIRED_COLUMNS

    return set()


def validate_columns(
    df: pd.DataFrame,
    import_type: str,
):

    required_columns = get_required_columns(
        import_type
    )

    actual_columns = set(
        df.columns
    )

    missing_columns = sorted(
        required_columns - actual_columns
    )

    if missing_columns:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Required columns are missing.",
                "missing_columns": missing_columns,
                "received_columns": list(df.columns),
            },
        )


# ============================================================
# Import History
# ============================================================

def get_import(
    db: Session,
    import_id: int,
    company_id: int,
) -> ImportHistory:

    import_history = (
        db.query(ImportHistory)
        .filter(
            ImportHistory.id == import_id,
            ImportHistory.company_id == company_id,
        )
        .first()
    )

    if not import_history:

        raise HTTPException(
            status_code=404,
            detail="Import record not found.",
        )

    return import_history


# ============================================================
# Stored File
# ============================================================

def get_stored_import_file(
    import_history: ImportHistory,
) -> str:

    folder = os.path.join(
        "exports",
        "imports",
    )

    if not os.path.exists(folder):

        raise HTTPException(
            status_code=404,
            detail="Stored import file not found.",
        )

    prefix = f"{import_history.company_id}_"

    matches = []

    for filename in os.listdir(folder):

        if (
            filename.startswith(prefix)
            and filename.endswith(
                import_history.filename
            )
        ):

            path = os.path.join(
                folder,
                filename,
            )

            if os.path.isfile(path):
                matches.append(path)

    if not matches:

        raise HTTPException(
            status_code=404,
            detail="Stored import file not found.",
        )

    return max(
        matches,
        key=os.path.getmtime,
    )


def load_import_dataframe(
    import_history: ImportHistory,
) -> pd.DataFrame:

    file_path = get_stored_import_file(
        import_history
    )

    with open(
        file_path,
        "rb",
    ) as file:

        file_bytes = file.read()

    return read_import_file(
        file_bytes=file_bytes,
        filename=import_history.filename,
    )


# ============================================================
# Upload Import
# ============================================================

def upload_import(
    db: Session,
    file: UploadFile,
    import_type: str,
    company_id: int,
    user_id: int,
):

    import_type = validate_import_type(
        import_type
    )

    filename = (
        file.filename
        or "uploaded_file"
    )

    file_bytes = file.file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    df = read_import_file(
        file_bytes=file_bytes,
        filename=filename,
    )

    validate_columns(
        df=df,
        import_type=import_type,
    )

    folder = os.path.join(
        "exports",
        "imports",
    )

    os.makedirs(
        folder,
        exist_ok=True,
    )

    stored_filename = (
        f"{company_id}_"
        f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_"
        f"{filename}"
    )

    stored_path = os.path.join(
        folder,
        stored_filename,
    )

    with open(
        stored_path,
        "wb",
    ) as stored_file:

        stored_file.write(
            file_bytes
        )

    import_history = ImportHistory(
        company_id=company_id,
        import_type=import_type,
        filename=filename,
        uploaded_by=user_id,
        total_records=len(df),
        successful_records=0,
        failed_records=0,
        duplicate_records=0,
        status="Pending",
    )

    db.add(
        import_history
    )

    db.commit()

    db.refresh(
        import_history
    )

    preview = (
        df.head(5)
        .fillna("")
        .astype(str)
        .to_dict(
            orient="records"
        )
    )

    return {
        "import_id": import_history.id,
        "import_type": import_type,
        "filename": filename,
        "columns": list(df.columns),
        "preview": preview,
        "total_records": len(df),
    }


# ============================================================
# Import Error
# ============================================================

def add_import_error(
    db: Session,
    import_id: int,
    row_number: int,
    error_type: str,
    error_message: str,
):

    error = ImportError(
        import_id=import_id,
        row_number=row_number,
        error_type=error_type,
        error_message=error_message,
    )

    db.add(error)


# ============================================================
# Product Validation
# ============================================================

def validate_product_row(
    db: Session,
    row: dict,
    company_id: int,
    seen_skus: set[str],
):

    sku = normalize_text(
        row.get("sku")
    )

    name = normalize_text(
        row.get("name")
    )

    category_name = normalize_text(
        row.get("category")
    )

    brand = normalize_text(
        row.get("brand")
    )

    price = parse_float(
        row.get("price")
    )

    stock = parse_int(
        row.get("stock")
    )

    if not sku:
        return False, "SKU is required."

    if not name:
        return False, "Product name is required."

    if not category_name:
        return False, "Category is required."

    if not brand:
        return False, "Brand is required."

    if price is None:
        return False, "Price must be a valid number."

    if price <= 0:
        return False, "Price must be greater than zero."

    if stock is None:
        return False, "Stock must be a valid integer."

    if stock < 0:
        return False, "Stock cannot be negative."

    if sku in seen_skus:

        return True, (
            "DUPLICATE: SKU appears multiple times in file."
        )

    existing_product = (
        db.query(Product)
        .filter(
            Product.company_id == company_id,
            Product.sku == sku,
        )
        .first()
    )

    if existing_product:

        return True, (
            "DUPLICATE: SKU already exists."
        )

    category = (
        db.query(Category)
        .filter(
            Category.company_id == company_id,
            Category.name.ilike(
                category_name
            ),
        )
        .first()
    )

    if not category:

        return False, (
            f"Category '{category_name}' "
            "does not exist."
        )

    return True, None


# ============================================================
# Customer Validation
# ============================================================

def validate_customer_row(
    db: Session,
    row: dict,
    company_id: int,
    seen_emails: set[str],
    seen_phones: set[str],
):

    name = normalize_text(
        row.get("name")
    )

    email = normalize_email(
        row.get("email")
    )

    phone = normalize_phone(
        row.get("phone")
    )

    if not name:
        return False, "Customer name is required."

    if not email:
        return False, "Email is required."

    if not validate_email(email):
        return False, "Invalid email address."

    if not phone:
        return False, "Phone number is required."

    if len(phone) < 7:
        return False, "Invalid phone number."

    if email in seen_emails:

        return True, (
            "DUPLICATE: Email appears multiple times in file."
        )

    if phone in seen_phones:

        return True, (
            "DUPLICATE: Phone appears multiple times in file."
        )

    existing_email = (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            Customer.email == email,
        )
        .first()
    )

    if existing_email:

        return True, (
            "DUPLICATE: Email already exists."
        )

    existing_phone = (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            Customer.phone == phone,
        )
        .first()
    )

    if existing_phone:

        return True, (
            "DUPLICATE: Phone already exists."
        )

    return True, None


# ============================================================
# Sales Validation
# ============================================================

def validate_sale_row(
    db: Session,
    row: dict,
    company_id: int,
    seen_invoices: set[str],
):

    invoice_number = normalize_text(
        row.get("invoice_number")
    )

    customer_email = normalize_email(
        row.get("customer_email")
    )

    sku = normalize_text(
        row.get("sku")
    )

    quantity = parse_int(
        row.get("quantity")
    )

    sales_channel = normalize_text(
        row.get("sales_channel")
    )

    payment_method = normalize_text(
        row.get("payment_method")
    )

    if not invoice_number:
        return False, "Invoice number is required."

    if not customer_email:
        return False, "Customer email is required."

    if not sku:
        return False, "SKU is required."

    if quantity is None:
        return False, "Quantity must be a valid integer."

    if quantity <= 0:
        return False, "Quantity must be greater than zero."

    if not sales_channel:
        return False, "Sales channel is required."

    if not payment_method:
        return False, "Payment method is required."

    if invoice_number in seen_invoices:
        return True, None

    existing_sale = (
        db.query(Sale)
        .filter(
            Sale.company_id == company_id,
            Sale.invoice_number == invoice_number,
        )
        .first()
    )

    if existing_sale:

        return True, (
            "DUPLICATE: Invoice number already exists."
        )

    customer = (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            Customer.email == customer_email,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if not customer:

        return False, (
            f"Customer with email "
            f"'{customer_email}' not found."
        )

    product = (
        db.query(Product)
        .filter(
            Product.company_id == company_id,
            Product.sku == sku,
            Product.is_active.is_(True),
        )
        .first()
    )

    if not product:

        return False, (
            f"Product with SKU "
            f"'{sku}' not found."
        )

    inventory = (
        db.query(Inventory)
        .filter(
            Inventory.company_id == company_id,
            Inventory.product_id == product.id,
        )
        .first()
    )

    if not inventory:

        return False, (
            f"Inventory not found for SKU '{sku}'."
        )

    if inventory.available_stock < quantity:

        return False, (
            f"Insufficient stock for SKU '{sku}'. "
            f"Available: {inventory.available_stock}, "
            f"Requested: {quantity}."
        )

    return True, None


# ============================================================
# Validate Import
# ============================================================

def validate_import(
    db: Session,
    import_id: int,
    company_id: int,
):

    import_history = get_import(
        db=db,
        import_id=import_id,
        company_id=company_id,
    )

    df = load_import_dataframe(
        import_history
    )

    validate_columns(
        df=df,
        import_type=import_history.import_type,
    )

    db.query(ImportError).filter(
        ImportError.import_id == import_id
    ).delete(
        synchronize_session=False
    )

    valid_records = 0
    invalid_records = 0
    duplicate_records = 0

    seen_skus = set()
    seen_emails = set()
    seen_phones = set()
    seen_invoices = set()

    for index, row in df.iterrows():

        row_number = index + 2

        row_data = row.to_dict()

        if import_history.import_type == "products":

            valid, message = validate_product_row(
                db=db,
                row=row_data,
                company_id=company_id,
                seen_skus=seen_skus,
            )

            sku = normalize_text(
                row_data.get("sku")
            )

            if sku:
                seen_skus.add(sku)

        elif import_history.import_type == "customers":

            valid, message = validate_customer_row(
                db=db,
                row=row_data,
                company_id=company_id,
                seen_emails=seen_emails,
                seen_phones=seen_phones,
            )

            email = normalize_email(
                row_data.get("email")
            )

            phone = normalize_phone(
                row_data.get("phone")
            )

            if email:
                seen_emails.add(email)

            if phone:
                seen_phones.add(phone)

        else:

            valid, message = validate_sale_row(
                db=db,
                row=row_data,
                company_id=company_id,
                seen_invoices=seen_invoices,
            )

            invoice = normalize_text(
                row_data.get("invoice_number")
            )

            if invoice:
                seen_invoices.add(invoice)

        if not valid:

            invalid_records += 1

            add_import_error(
                db=db,
                import_id=import_id,
                row_number=row_number,
                error_type="VALIDATION",
                error_message=message,
            )

        elif message and message.startswith(
            "DUPLICATE:"
        ):

            duplicate_records += 1

            add_import_error(
                db=db,
                import_id=import_id,
                row_number=row_number,
                error_type="DUPLICATE",
                error_message=message,
            )

        else:

            valid_records += 1

    import_history.failed_records = (
        invalid_records
    )

    import_history.duplicate_records = (
        duplicate_records
    )

    if invalid_records == 0:
        import_history.status = "Validated"
    else:
        import_history.status = "Validation Failed"

    db.commit()

    errors = (
        db.query(ImportError)
        .filter(
            ImportError.import_id == import_id
        )
        .order_by(
            ImportError.row_number.asc()
        )
        .all()
    )

    return {
        "import_id": import_id,
        "total_records": len(df),
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "duplicate_records": duplicate_records,
        "columns": list(df.columns),
        "errors": [
            {
                "row_number": error.row_number,
                "error_type": error.error_type,
                "error_message": error.error_message,
            }
            for error in errors
        ],
    }


# ============================================================
# Customer ID
# ============================================================

def generate_customer_id(
    db: Session,
) -> str:

    last_customer = (
        db.query(Customer)
        .order_by(
            Customer.id.desc()
        )
        .first()
    )

    if not last_customer:
        return "CUS0001"

    try:

        last_number = int(
            last_customer.customer_id.replace(
                "CUS",
                "",
            )
        )

    except (
        ValueError,
        AttributeError,
    ):

        last_number = last_customer.id

    return (
        f"CUS{last_number + 1:04d}"
    )


# ============================================================
# Process Products
# ============================================================

def process_product_import(
    db: Session,
    df: pd.DataFrame,
    company_id: int,
    user_id: int,
    import_id: int,
):

    successful = 0
    failed = 0
    duplicates = 0

    for index, row in df.iterrows():

        row_number = index + 2
        row_data = row.to_dict()

        try:

            # Each row gets its own SAVEPOINT.
            # A failed row will not destroy successful rows.
            with db.begin_nested():

                sku = normalize_text(
                    row_data.get("sku")
                )

                existing = (
                    db.query(Product)
                    .filter(
                        Product.company_id == company_id,
                        Product.sku == sku,
                    )
                    .first()
                )

                if existing:

                    duplicates += 1
                    continue

                category_name = normalize_text(
                    row_data.get("category")
                )

                category = (
                    db.query(Category)
                    .filter(
                        Category.company_id == company_id,
                        Category.name.ilike(
                            category_name
                        ),
                    )
                    .first()
                )

                if not category:

                    raise ValueError(
                        f"Category '{category_name}' not found."
                    )

                price = parse_float(
                    row_data.get("price")
                )

                stock = parse_int(
                    row_data.get("stock")
                )

                if price is None:
                    raise ValueError(
                        "Invalid product price."
                    )

                if stock is None:
                    raise ValueError(
                        "Invalid stock quantity."
                    )

                status = calculate_stock_status(
                    stock
                )

                product = Product(
                    company_id=company_id,
                    category_id=category.id,
                    name=normalize_text(
                        row_data.get("name")
                    ),
                    sku=sku,
                    description=normalize_text(
                        row_data.get("description")
                    ),
                    brand=normalize_text(
                        row_data.get("brand")
                    ),
                    unit_price=price,
                    stock_quantity=stock,
                    status=status,
                    is_active=True,
                )

                db.add(product)
                db.flush()

                inventory = Inventory(
                    company_id=company_id,
                    product_id=product.id,
                    current_stock=stock,
                    reserved_stock=0,
                    available_stock=stock,
                    reorder_level=10,
                    stock_status=status,
                )

                db.add(inventory)

            successful += 1

        except Exception as exc:

            failed += 1

            error_message = str(exc)

            if "customer_purchase_summary_customer_id_key" in error_message:
                error_message = (
                    "Customer purchase summary already exists."
                )

            elif "customer_id" in error_message and "UniqueViolation" in error_message:
                error_message = (
                    "Customer summary already exists for this customer."
                )

            elif "UniqueViolation" in error_message:
                error_message = (
                    "Duplicate record already exists."
                )

            else:
                error_message = (
                    "Unable to process customer record."
                )

            add_import_error(
                db=db,
                import_id=import_id,
                row_number=row_number,
                error_type="PROCESSING",
                error_message=error_message,
            )

    return (
        successful,
        failed,
        duplicates,
    )


# ============================================================
# Process Customers
# ============================================================

def process_customer_import(
    db: Session,
    df: pd.DataFrame,
    company_id: int,
    user_id: int,
    import_id: int,
):

    successful = 0
    failed = 0
    duplicates = 0

    for index, row in df.iterrows():

        row_number = index + 2
        row_data = row.to_dict()

        try:

            with db.begin_nested():

                email = normalize_email(
                    row_data.get("email")
                )

                phone = normalize_phone(
                    row_data.get("phone")
                )

                # ------------------------------------------------
                # Check duplicate customer
                # ------------------------------------------------

                existing = (
                    db.query(Customer)
                    .filter(
                        Customer.company_id == company_id,
                        (
                            (Customer.email == email)
                            |
                            (Customer.phone == phone)
                        ),
                        Customer.deleted_at.is_(None),
                    )
                    .first()
                )

                if existing:

                    duplicates += 1
                    continue

                # ------------------------------------------------
                # Customer Name
                # ------------------------------------------------

                first_name, last_name = (
                    split_customer_name(
                        row_data.get("name")
                    )
                )

                # ------------------------------------------------
                # Create Customer
                # ------------------------------------------------

                customer = Customer(
                    company_id=company_id,
                    customer_id=generate_customer_id(
                        db
                    ),
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    address=normalize_text(
                        row_data.get("address")
                    ) or "Not Provided",
                    city=normalize_text(
                        row_data.get("city")
                    ) or "Not Provided",
                    state=normalize_text(
                        row_data.get("state")
                    ) or "Not Provided",
                    country=normalize_text(
                        row_data.get("country")
                    ) or "India",
                    postal_code=normalize_text(
                        row_data.get("postal_code")
                    ) or "000000",
                    segment="New",
                    status="Active",
                    total_orders=0,
                    total_spend=0,
                )

                db.add(customer)
                db.flush()

                # ------------------------------------------------
                # Customer Purchase Summary
                #
                # IMPORTANT:
                # Do not blindly INSERT a summary.
                # A customer can already have one.
                # ------------------------------------------------

                summary = (
                    db.query(
                        CustomerPurchaseSummary
                    )
                    .filter(
                        CustomerPurchaseSummary.customer_id
                        == customer.id
                    )
                    .first()
                )

                if summary is None:

                    summary = CustomerPurchaseSummary(
                        customer_id=customer.id,
                        total_orders=0,
                        total_revenue=0,
                        total_products_purchased=0,
                        average_order_value=0,
                        purchase_frequency=0,
                        segment="New Customer",
                    )

                    db.add(summary)

                # ------------------------------------------------
                # Customer Timeline
                # ------------------------------------------------

                timeline = CustomerTimeline(
                    customer_id=customer.id,
                    event="Customer Imported",
                    description=(
                        f"Customer imported from "
                        f"{normalize_text(row_data.get('name'))}."
                    ),
                )

                db.add(timeline)

                db.flush()

            successful += 1

        except Exception as exc:

            failed += 1

            # Never expose raw database/SQL errors.
            error_message = str(exc)

            if "customer_purchase_summary_customer_id_key" in error_message:
                error_message = (
                    "Customer purchase summary already exists."
                )

            elif "UniqueViolation" in error_message:
                error_message = (
                    "A customer with the same unique information "
                    "already exists."
                )

            elif "duplicate key" in error_message.lower():
                error_message = (
                    "Duplicate customer record."
                )

            add_import_error(
                db=db,
                import_id=import_id,
                row_number=row_number,
                error_type="PROCESSING",
                error_message=error_message,
            )

    return (
        successful,
        failed,
        duplicates,
    )


# ============================================================
# Process Sales
# ============================================================

def process_sales_import(
    db: Session,
    df: pd.DataFrame,
    company_id: int,
    user_id: int,
    import_id: int,
):

    successful = 0
    failed = 0
    duplicates = 0

    grouped = df.groupby(
        "invoice_number",
        sort=False,
    )

    for invoice_number, invoice_rows in grouped:

        invoice_number = normalize_text(
            invoice_number
        )

        # First spreadsheet row for error reporting.
        first_index = invoice_rows.index[0]

        row_number = first_index + 2

        try:

            with db.begin_nested():

                existing_sale = (
                    db.query(Sale)
                    .filter(
                        Sale.company_id == company_id,
                        Sale.invoice_number
                        == invoice_number,
                    )
                    .first()
                )

                if existing_sale:

                    duplicates += len(
                        invoice_rows
                    )

                    continue

                first_row = (
                    invoice_rows.iloc[0]
                )

                customer_email = normalize_email(
                    first_row.get(
                        "customer_email"
                    )
                )

                customer = (
                    db.query(Customer)
                    .filter(
                        Customer.company_id
                        == company_id,
                        Customer.email
                        == customer_email,
                        Customer.deleted_at.is_(None),
                    )
                    .first()
                )

                if not customer:

                    raise ValueError(
                        f"Customer with email "
                        f"'{customer_email}' not found."
                    )

                sale = Sale(
                    company_id=company_id,
                    invoice_number=invoice_number,
                    customer_id=customer.id,
                    customer_name=(
                        f"{customer.first_name} "
                        f"{customer.last_name}"
                    ),
                    sale_date=datetime.utcnow(),
                    sales_channel=normalize_text(
                        first_row.get(
                            "sales_channel"
                        )
                    ),
                    payment_method=normalize_text(
                        first_row.get(
                            "payment_method"
                        )
                    ),
                    discount=0,
                    tax=0,
                    total_amount=0,
                    status="Paid",
                    created_by=user_id,
                )

                db.add(sale)
                db.flush()

                subtotal = 0
                product_count = 0

                for _, row in invoice_rows.iterrows():

                    sku = normalize_text(
                        row.get("sku")
                    )

                    quantity = parse_int(
                        row.get("quantity")
                    )

                    if quantity is None:
                        raise ValueError(
                            f"Invalid quantity for SKU '{sku}'."
                        )

                    product = (
                        db.query(Product)
                        .filter(
                            Product.company_id
                            == company_id,
                            Product.sku == sku,
                            Product.is_active.is_(True),
                        )
                        .first()
                    )

                    if not product:

                        raise ValueError(
                            f"Product SKU "
                            f"'{sku}' not found."
                        )

                    inventory = (
                        db.query(Inventory)
                        .filter(
                            Inventory.company_id
                            == company_id,
                            Inventory.product_id
                            == product.id,
                        )
                        .with_for_update()
                        .first()
                    )

                    if not inventory:

                        raise ValueError(
                            f"Inventory not found "
                            f"for SKU '{sku}'."
                        )

                    if inventory.available_stock < quantity:

                        raise ValueError(
                            f"Insufficient stock for "
                            f"'{product.name}'. "
                            f"Available: "
                            f"{inventory.available_stock}, "
                            f"Requested: {quantity}."
                        )

                    unit_price = float(
                        product.unit_price
                    )

                    line_total = (
                        quantity
                        * unit_price
                    )

                    sale_item = SaleItem(
                        sale_id=sale.id,
                        product_id=product.id,
                        category_id=product.category_id,
                        quantity=quantity,
                        unit_price=unit_price,
                        discount=0,
                        tax=0,
                        total=line_total,
                    )

                    db.add(sale_item)

                    previous_stock = (
                        inventory.current_stock
                    )

                    inventory.current_stock = max(
                        0,
                        inventory.current_stock
                        - quantity,
                    )

                    inventory.available_stock = max(
                        0,
                        inventory.available_stock
                        - quantity,
                    )

                    inventory.stock_status = (
                        calculate_stock_status(
                            inventory.available_stock,
                            inventory.reorder_level,
                        )
                    )

                    product.stock_quantity = (
                        inventory.current_stock
                    )

                    product.status = (
                        inventory.stock_status
                    )

                    movement = InventoryMovement(
                        inventory_id=inventory.id,
                        movement_type="OUT",
                        quantity_changed=quantity,
                        previous_quantity=previous_stock,
                        updated_quantity=(
                            inventory.current_stock
                        ),
                        reason="Imported Sale",
                        remarks=(
                            f"Invoice "
                            f"{invoice_number}"
                        ),
                        performed_by=user_id,
                    )

                    db.add(movement)

                    subtotal += line_total
                    product_count += quantity

                sale.total_amount = subtotal

                customer.total_orders = (
                    (customer.total_orders or 0)
                    + 1
                )

                customer.total_spend = (
                    (customer.total_spend or 0)
                    + subtotal
                )

                customer.last_purchase_date = (
                    datetime.utcnow()
                )

                summary = (
                    db.query(
                        CustomerPurchaseSummary
                    )
                    .filter(
                        CustomerPurchaseSummary.customer_id
                        == customer.id
                    )
                    .first()
                )

                if summary is None:

                    summary = (
                        CustomerPurchaseSummary(
                            customer_id=customer.id,
                        )
                    )

                    db.add(summary)

                summary.total_orders = (
                    customer.total_orders
                )

                summary.total_revenue = (
                    customer.total_spend
                )

                summary.total_products_purchased = (
                    (summary.total_products_purchased or 0)
                    + product_count
                )

                summary.average_order_value = (
                    summary.total_revenue
                    / summary.total_orders
                    if summary.total_orders
                    else 0
                )

                summary.purchase_frequency = (
                    float(
                        summary.total_orders
                    )
                )

                if not summary.first_purchase_date:

                    summary.first_purchase_date = (
                        datetime.utcnow().date()
                    )

                summary.last_purchase_date = (
                    datetime.utcnow().date()
                )

                if summary.total_orders > 10:

                    summary.segment = (
                        "VIP Customer"
                    )

                elif summary.total_orders > 5:

                    summary.segment = (
                        "Loyal Customer"
                    )

                elif summary.total_orders > 0:

                    summary.segment = (
                        "Regular Customer"
                    )

                else:

                    summary.segment = (
                        "New Customer"
                    )

                timeline = CustomerTimeline(
                    customer_id=customer.id,
                    event="Sale Imported",
                    description=(
                        f"Imported invoice "
                        f"{invoice_number}."
                    ),
                )

                db.add(timeline)

            successful += len(
                invoice_rows
            )

        except Exception as exc:

            failed += len(
                invoice_rows
            )

            add_import_error(
                db=db,
                import_id=import_id,
                row_number=row_number,
                error_type="PROCESSING",
                error_message=str(exc),
            )

    return (
        successful,
        failed,
        duplicates,
    )


# ============================================================
# Process Import
# ============================================================

def process_import(
    db: Session,
    import_id: int,
    company_id: int,
    user_id: int,
):
    import_history = get_import(
        db=db,
        import_id=import_id,
        company_id=company_id,
    )

    validation = validate_import(
        db=db,
        import_id=import_id,
        company_id=company_id,
    )

    if validation["invalid_records"] > 0:
        import_history.status = "Validation Failed"

        db.commit()

        NotificationService.create_notification(
            db=db,
            company_id=company_id,
            user_id=user_id,
            notification_type="IMPORT_FAILED",
            title="Import Failed",
            message=f"{import_history.import_type.title()} import failed validation. {validation['invalid_records']} records contain validation errors.",
            priority="HIGH",
            resource_type="Import",
            resource_id=import_id,
            dedupe_key=f"import:{import_id}:failed",
        )

        return {
            "import_id": import_id,
            "status": "Validation Failed",
            "total_records": validation["total_records"],
            "successful_records": 0,
            "failed_records": validation["invalid_records"],
            "duplicate_records": validation["duplicate_records"],
            "validation_failures": validation["invalid_records"],
        }

    df = load_import_dataframe(
        import_history
    )

    import_history.status = "Processing"

    db.commit()

    if import_history.import_type == "products":
        (
            successful_records,
            failed_records,
            duplicate_records,
        ) = process_product_import(
            db=db,
            df=df,
            company_id=company_id,
            user_id=user_id,
            import_id=import_id,
        )

    elif import_history.import_type == "customers":
        (
            successful_records,
            failed_records,
            duplicate_records,
        ) = process_customer_import(
            db=db,
            df=df,
            company_id=company_id,
            user_id=user_id,
            import_id=import_id,
        )

    else:
        (
            successful_records,
            failed_records,
            duplicate_records,
        ) = process_sales_import(
            db=db,
            df=df,
            company_id=company_id,
            user_id=user_id,
            import_id=import_id,
        )

    import_history.successful_records = successful_records
    import_history.failed_records = failed_records
    import_history.duplicate_records = duplicate_records
    import_history.completed_at = datetime.utcnow()

    if failed_records == 0:
        import_history.status = "Completed"
    elif successful_records > 0:
        import_history.status = "Completed With Errors"
    else:
        import_history.status = "Failed"

    db.commit()
    db.refresh(import_history)

    if import_history.status == "Completed":
        NotificationService.create_notification(
            db=db,
            company_id=company_id,
            user_id=user_id,
            notification_type="IMPORT_COMPLETED",
            title="Import Completed",
            message=f"{import_history.import_type.title()} import completed successfully. {successful_records} records were imported.",
            priority="MEDIUM",
            resource_type="Import",
            resource_id=import_id,
            dedupe_key=f"import:{import_id}:completed",
        )

    elif import_history.status == "Completed With Errors":
        NotificationService.create_notification(
            db=db,
            company_id=company_id,
            user_id=user_id,
            notification_type="IMPORT_FAILED",
            title="Import Completed With Errors",
            message=f"{import_history.import_type.title()} import completed with errors. {successful_records} records succeeded and {failed_records} records failed.",
            priority="HIGH",
            resource_type="Import",
            resource_id=import_id,
            dedupe_key=f"import:{import_id}:completed-with-errors",
        )

    else:
        NotificationService.create_notification(
            db=db,
            company_id=company_id,
            user_id=user_id,
            notification_type="IMPORT_FAILED",
            title="Import Failed",
            message=f"{import_history.import_type.title()} import failed. {failed_records} records could not be imported.",
            priority="CRITICAL",
            resource_type="Import",
            resource_id=import_id,
            dedupe_key=f"import:{import_id}:failed",
        )

    return {
        "import_id": import_id,
        "status": import_history.status,
        "total_records": import_history.total_records,
        "successful_records": successful_records,
        "failed_records": failed_records,
        "duplicate_records": duplicate_records,
        "validation_failures": 0,
    }

# ============================================================
# Import History
# ============================================================

def get_import_history(
    db: Session,
    company_id: int,
):

    return (
        db.query(ImportHistory)
        .filter(
            ImportHistory.company_id
            == company_id
        )
        .order_by(
            ImportHistory.created_at.desc()
        )
        .all()
    )


# ============================================================
# Import Details
# ============================================================

def get_import_details(
    db: Session,
    import_id: int,
    company_id: int,
):

    import_history = get_import(
        db=db,
        import_id=import_id,
        company_id=company_id,
    )

    errors = (
        db.query(ImportError)
        .filter(
            ImportError.import_id
            == import_id
        )
        .order_by(
            ImportError.row_number.asc()
        )
        .all()
    )

    return {
        "id": import_history.id,
        "company_id": import_history.company_id,
        "import_type": import_history.import_type,
        "filename": import_history.filename,
        "uploaded_by": import_history.uploaded_by,
        "total_records": import_history.total_records,
        "successful_records": (
            import_history.successful_records
        ),
        "failed_records": (
            import_history.failed_records
        ),
        "duplicate_records": (
            import_history.duplicate_records
        ),
        "status": import_history.status,
        "created_at": import_history.created_at,
        "completed_at": import_history.completed_at,
        "errors": [
            {
                "row_number": error.row_number,
                "error_type": error.error_type,
                "error_message": error.error_message,
            }
            for error in errors
        ],
    }


def download_failed_records(
    db: Session,
    import_id: int,
    company_id: int,
):
    import_history = get_import(
        db=db,
        import_id=import_id,
        company_id=company_id,
    )

    errors = (
        db.query(ImportError)
        .filter(
            ImportError.import_id == import_id,
            ImportError.error_type.in_(
                ["VALIDATION", "PROCESSING"]
            ),
        )
        .order_by(
            ImportError.row_number.asc()
        )
        .all()
    )

    if not errors:
        raise HTTPException(
            status_code=404,
            detail="No failed records found for this import.",
        )

    df = load_import_dataframe(
        import_history
    )

    failed_rows = []

    for error in errors:
        dataframe_index = error.row_number - 2

        if (
            dataframe_index < 0
            or dataframe_index >= len(df)
        ):
            continue

        row = df.iloc[dataframe_index].to_dict()

        row["row_number"] = error.row_number
        row["error_type"] = error.error_type
        row["error_message"] = error.error_message

        failed_rows.append(row)

    if not failed_rows:
        raise HTTPException(
            status_code=404,
            detail="Failed record data could not be found.",
        )

    failed_df = pd.DataFrame(
        failed_rows
    )

    columns = [
        "row_number",
        *list(df.columns),
        "error_type",
        "error_message",
    ]

    failed_df = failed_df[
        [
            column
            for column in columns
            if column in failed_df.columns
        ]
    ]

    output = StringIO()

    failed_df.to_csv(
        output,
        index=False,
    )

    filename = (
        f"failed_records_{import_history.id}.csv"
    )

    return (
        output.getvalue().encode("utf-8"),
        filename,
    )