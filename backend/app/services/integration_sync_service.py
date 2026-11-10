import csv
import json

from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.integration import Integration
from app.models.integration_mapping import IntegrationMapping
from app.models.integration_sync import IntegrationSync
from app.models.integration_sync_error import IntegrationSyncError
from app.models.product import Product
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement

from app.services.integration_service import (
    INTEGRATION_STORAGE,
    get_integration_by_id,
)

from app.services.integration_rest_service import fetch_rest_api_records

from app.services.audit_service import create_audit_log
from app.utils.inventory_utils import calculate_stock_status


def _utc_now():
    return datetime.now(timezone.utc)


def _get_csv_path(integration):
    metadata = (
        integration.connection_config or {}
    ).get("csv_file")

    if not metadata:
        raise ValueError("No CSV file uploaded.")

    relative_path = Path(metadata.get("storage_path", ""))

    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("Invalid CSV storage path.")

    storage_root = INTEGRATION_STORAGE.resolve()
    file_path = (storage_root / relative_path).resolve()

    if not file_path.is_relative_to(storage_root):
        raise ValueError("Invalid CSV storage path.")

    if not file_path.is_file():
        raise ValueError("Uploaded CSV file not found.")

    return file_path


def _read_csv_records(file_path):
    records = []

    try:
        with file_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file, strict=True)

            if not reader.fieldnames:
                raise ValueError("CSV headers are missing.")

            headers = [
                header.strip()
                for header in reader.fieldnames
            ]

            if any(not header for header in headers):
                raise ValueError("CSV contains empty headers.")

            if len(headers) != len(set(headers)):
                raise ValueError("CSV contains duplicate headers.")

            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    records.append({
                        "row_number": row_number,
                        "data": {},
                        "row_error": "Row contains more values than headers.",
                    })
                    continue

                normalized = {
                    header: (row.get(original) or "").strip()
                    for original, header in zip(
                        reader.fieldnames,
                        headers,
                    )
                }

                if not any(normalized.values()):
                    continue

                records.append({
                    "row_number": row_number,
                    "data": normalized,
                    "row_error": None,
                })

    except csv.Error as exc:
        raise ValueError(f"Invalid CSV format: {str(exc)}")

    return records


def _get_source_records(integration):
    if integration.source_type == "csv":
        file_path = _get_csv_path(integration)
        return _read_csv_records(file_path)

    if integration.source_type == "rest_api":
        records = fetch_rest_api_records(integration)

        return [
            {
                "row_number": index,
                "data": record,
                "row_error": None,
            }
            for index, record in enumerate(records, start=1)
        ]

    raise ValueError(
        f"Unsupported integration source type: {integration.source_type}"
    )


def _parse_boolean(value):
    if value is None or value == "":
        return True

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes"}:
        return True

    if normalized in {"false", "0", "no"}:
        return False

    raise ValueError("Invalid is_active value. Use true or false.")


def _map_product_record(source_data, mappings):
    mapped = {}

    for mapping in mappings:
        value = source_data.get(mapping.source_field)

        if isinstance(value, str):
            value = value.strip()

        if mapping.is_required and value in (None, ""):
            if mapping.target_field != "brand":
                raise ValueError(
                    f"Required field '{mapping.source_field}' is empty."
                )

        if value in (None, ""):
            mapped[mapping.target_field] = None
            continue

        config = mapping.transformation_config or {}
        operation = config.get("operation")

        if operation == "uppercase":
            value = str(value).upper()

        elif operation == "lowercase":
            value = str(value).lower()

        elif operation == "trim":
            value = str(value).strip()

        elif operation == "prefix":
            value = f"{config.get('value', '')}{value}"

        elif operation == "suffix":
            value = f"{value}{config.get('value', '')}"

        mapped[mapping.target_field] = value

    required_fields = {
        "sku",
        "name",
        "category_id",
        "unit_price",
        "stock_quantity",
    }

    missing = [
        field
        for field in required_fields
        if mapped.get(field) in (None, "")
    ]

    if missing:
        raise ValueError(
            f"Missing required fields: {', '.join(sorted(missing))}."
        )

    for field in ("sku", "name"):
        mapped[field] = str(mapped.get(field) or "").strip()

    mapped["brand"] = str(mapped.get("brand") or "Generic").strip()

    if not mapped["sku"]:
        raise ValueError("SKU cannot be empty.")

    if not mapped["name"]:
        raise ValueError("Product name cannot be empty.")

    if not mapped["brand"]:
        mapped["brand"] = "Generic"

    try:
        price = Decimal(str(mapped["unit_price"]))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Unit price must be a valid number.")

    if not price.is_finite() or price < 0:
        raise ValueError(
            "Unit price must be a non-negative finite number."
        )

    mapped["unit_price"] = float(price)

    raw_quantity = mapped["stock_quantity"]

    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        raise ValueError("Stock quantity must be an integer.")

    if isinstance(raw_quantity, float) and not raw_quantity.is_integer():
        raise ValueError("Stock quantity must be an integer.")

    if isinstance(raw_quantity, str):
        if str(quantity) != raw_quantity.strip():
            raise ValueError("Stock quantity must be an integer.")

    if quantity < 0:
        raise ValueError("Stock quantity cannot be negative.")

    mapped["stock_quantity"] = quantity

    mapped["category_name"] = str(
        mapped["category_id"]
    ).strip()

    mapped["is_active"] = _parse_boolean(
        mapped.get("is_active")
    )

    return mapped


def _resolve_category(db, category_name, company_id):
    category_name = str(category_name or "").strip()

    if not category_name:
        raise ValueError("Category name cannot be empty.")

    categories = (
        db.query(Category)
        .filter(
            Category.company_id == company_id,
            Category.name.ilike(category_name),
        )
        .with_for_update()
        .all()
    )

    if len(categories) > 1:
        raise ValueError(
            f"Multiple categories named '{category_name}' exist."
        )

    if categories:
        return categories[0]

    category = Category(
        company_id=company_id,
        name=category_name,
        description="Created automatically during data integration.",
    )

    db.add(category)
    db.flush()

    return category


def _record_sync_error(
    db,
    sync_id,
    row_number,
    source_data,
    error_message,
):
    source_data = (
        source_data
        if isinstance(source_data, dict)
        else {}
    )

    db.add(
        IntegrationSyncError(
            sync_id=sync_id,
            source_record_id=(
                str(source_data.get("sku"))
                if source_data.get("sku")
                else None
            ),
            row_number=row_number,
            error_category="VALIDATION_OR_SYNC_ERROR",
            error_message=str(error_message)[:2000],
            source_data=source_data,
            retry_status="pending",
            retry_count=0,
            is_retryable=True,
        )
    )


def _get_or_create_inventory(
    db,
    product,
    company_id,
    user_id,
):
    inventory = (
        db.query(Inventory)
        .filter(
            Inventory.product_id == product.id,
            Inventory.company_id == company_id,
        )
        .with_for_update()
        .first()
    )

    if inventory:
        return inventory

    initial_quantity = product.stock_quantity or 0

    inventory = Inventory(
        company_id=company_id,
        product_id=product.id,
        current_stock=initial_quantity,
        reserved_stock=0,
        available_stock=initial_quantity,
        reorder_level=10,
        stock_status=calculate_stock_status(
            initial_quantity,
            10,
        ),
    )

    db.add(inventory)
    db.flush()

    if initial_quantity > 0:
        db.add(
            InventoryMovement(
                inventory_id=inventory.id,
                movement_type="Stock Addition",
                quantity_changed=initial_quantity,
                previous_quantity=0,
                updated_quantity=initial_quantity,
                reason="Inventory initialized through integration",
                remarks="Inventory record created during synchronization.",
                performed_by=user_id,
            )
        )

    return inventory


def _create_inventory(
    db,
    product,
    company_id,
    user_id,
    quantity,
):
    inventory = Inventory(
        company_id=company_id,
        product_id=product.id,
        current_stock=quantity,
        reserved_stock=0,
        available_stock=quantity,
        reorder_level=10,
        stock_status=calculate_stock_status(
            quantity,
            10,
        ),
    )

    db.add(inventory)
    db.flush()

    if quantity > 0:
        db.add(
            InventoryMovement(
                inventory_id=inventory.id,
                movement_type="Stock Addition",
                quantity_changed=quantity,
                previous_quantity=0,
                updated_quantity=quantity,
                reason="Initial stock through integration",
                remarks="Initial product stock imported through integration.",
                performed_by=user_id,
            )
        )

    return inventory


def _update_product(
    db,
    product,
    inventory,
    mapped,
    user_id,
):
    new_quantity = mapped["stock_quantity"]

    if new_quantity < inventory.reserved_stock:
        raise ValueError(
            "Imported stock cannot be lower than reserved stock."
        )

    previous_quantity = inventory.current_stock

    product.name = mapped["name"]
    product.category_id = mapped["category_id"]
    product.brand = mapped["brand"]
    product.unit_price = mapped["unit_price"]
    product.description = mapped.get("description")
    product.stock_quantity = new_quantity
    product.is_active = mapped["is_active"]

    if mapped.get("status"):
        product.status = mapped["status"]

    inventory.current_stock = new_quantity
    inventory.available_stock = (
        new_quantity - inventory.reserved_stock
    )

    inventory.stock_status = calculate_stock_status(
        inventory.available_stock,
        inventory.reorder_level,
    )

    difference = new_quantity - previous_quantity

    if difference:
        db.add(
            InventoryMovement(
                inventory_id=inventory.id,
                movement_type="Integration Adjustment",
                quantity_changed=abs(difference),
                previous_quantity=previous_quantity,
                updated_quantity=new_quantity,
                reason="Stock updated through integration",
                remarks="Product stock synchronized through integration.",
                performed_by=user_id,
            )
        )


def _process_product_record(
    db,
    source_data,
    mappings,
    company_id,
    user_id,
    strategy,
):
    mapped = _map_product_record(
        source_data,
        mappings,
    )

    sku = mapped["sku"]

    category = _resolve_category(
        db,
        mapped["category_name"],
        company_id,
    )

    mapped["category_id"] = category.id

    product = (
        db.query(Product)
        .filter(Product.sku == sku)
        .with_for_update()
        .first()
    )

    if product and product.company_id != company_id:
        raise ValueError(
            f"SKU '{sku}' belongs to another company."
        )

    if product:
        if strategy in {"insert", "reject"}:
            raise ValueError(
                f"SKU '{sku}' already exists."
            )

        if strategy == "skip":
            return "skipped"

        inventory = _get_or_create_inventory(
            db,
            product,
            company_id,
            user_id,
        )

        _update_product(
            db,
            product,
            inventory,
            mapped,
            user_id,
        )

        db.flush()

        return "updated"

    product = Product(
        company_id=company_id,
        category_id=mapped["category_id"],
        name=mapped["name"],
        sku=sku,
        description=mapped.get("description"),
        brand=mapped["brand"],
        unit_price=mapped["unit_price"],
        stock_quantity=mapped["stock_quantity"],
        status=mapped.get("status") or "In Stock",
        is_active=mapped["is_active"],
    )

    db.add(product)
    db.flush()

    _create_inventory(
        db,
        product,
        company_id,
        user_id,
        mapped["stock_quantity"],
    )

    db.flush()

    return "inserted"


def _get_source_updated_at(source_data, field_path):
    if not field_path:
        return None

    value = source_data

    for key in field_path.split("."):
        if not isinstance(value, dict):
            return None

        value = value.get(key)

    if not value:
        return None

    try:
        timestamp = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return timestamp.astimezone(timezone.utc)

    except (TypeError, ValueError):
        return None


def _get_latest_source_timestamp(records, field_path):
    timestamps = []

    for record in records:
        timestamp = _get_source_updated_at(
            record["data"],
            field_path,
        )

        if timestamp:
            timestamps.append(timestamp)

    return max(timestamps) if timestamps else None


def _get_mappings(db, integration_id):
    return (
        db.query(IntegrationMapping)
        .filter(
            IntegrationMapping.integration_id == integration_id,
            IntegrationMapping.is_active.is_(True),
        )
        .order_by(IntegrationMapping.id.asc())
        .all()
    )


def _create_sync_audit(
    db,
    company_id,
    user_id,
    sync,
    integration,
    trigger_type,
    inserted,
    updated,
    skipped,
    failed,
    ip_address,
    user_agent,
):
    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Integration",
        action="UPDATE",
        resource_type="IntegrationSync",
        resource_id=str(sync.id),
        description=(
            f"Product synchronization finished. "
            f"Trigger: {trigger_type}. "
            f"Inserted: {inserted}, Updated: {updated}, "
            f"Skipped: {skipped}, Failed: {failed}."
        ),
        after_values={
            "status": sync.status,
            "trigger_type": trigger_type,
            "source_type": integration.source_type,
            "total_records": sync.total_records,
            "inserted_records": inserted,
            "updated_records": updated,
            "skipped_records": skipped,
            "failed_records": failed,
        },
        ip_address=ip_address,
        user_agent=user_agent,
        status="SUCCESS" if failed == 0 else "FAILED",
    )


def synchronize_products(
    db: Session,
    integration_id: int,
    company_id: int,
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
    trigger_type: str = "manual",
):
    if trigger_type not in {
        "manual",
        "scheduled",
        "initial",
        "incremental",
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid synchronization trigger type.",
        )

    integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    if integration.source_type not in {"csv", "rest_api"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported integration source type.",
        )

    if integration.target_module != "products":
        raise HTTPException(
            status_code=400,
            detail="This service supports product synchronization only.",
        )

    if not integration.is_enabled:
        raise HTTPException(
            status_code=400,
            detail="Enable the integration before synchronization.",
        )

    strategy = integration.sync_strategy

    if strategy not in {"insert", "update", "skip", "reject"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid duplicate handling strategy.",
        )

    try:
        mappings = _get_mappings(
            db,
            integration_id,
        )

        if not mappings:
            raise ValueError(
                "Configure field mappings before synchronization."
            )

        source_records = _get_source_records(integration)

        if not source_records:
            raise ValueError("Source contains no records.")

        config = integration.connection_config or {}
        incremental_config = config.get("incremental") or {}

        updated_at_field = incremental_config.get(
            "updated_at_field"
        )

        previous_watermark = integration.last_source_sync_at

        if (
            previous_watermark
            and previous_watermark.tzinfo is None
        ):
            previous_watermark = previous_watermark.replace(
                tzinfo=timezone.utc
            )

        if trigger_type == "incremental":
            if integration.source_type != "rest_api":
                raise ValueError(
                    "Timestamp-based incremental synchronization "
                    "is currently supported only for REST API."
                )

            if not incremental_config.get("enabled"):
                raise ValueError(
                    "Incremental synchronization is not enabled."
                )

            if not updated_at_field:
                raise ValueError(
                    "Configure the source updated timestamp field."
                )

            if previous_watermark:
                records = []

                for record in source_records:
                    source_timestamp = _get_source_updated_at(
                        record["data"],
                        updated_at_field,
                    )

                    if source_timestamp is None:
                        records.append(record)
                    elif source_timestamp > previous_watermark:
                        records.append(record)
            else:
                records = source_records

            strategy = "update"

        else:
            records = source_records

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve integration source records.",
        )

    sync = IntegrationSync(
        integration_id=integration.id,
        company_id=company_id,
        triggered_by=user_id,
        trigger_type=trigger_type,
        status="running",
        total_records=len(records),
        processed_records=0,
        inserted_records=0,
        updated_records=0,
        skipped_records=0,
        failed_records=0,
        started_at=_utc_now(),
    )

    db.add(sync)
    db.commit()
    db.refresh(sync)

    inserted = 0
    updated = 0
    skipped = 0
    failed = 0
    processed = 0

    seen_skus = set()

    try:
        for record in records:
            row_number = record["row_number"]
            source_data = record["data"]

            processed += 1

            try:
                if record["row_error"]:
                    raise ValueError(record["row_error"])

                if trigger_type == "incremental":
                    source_timestamp = _get_source_updated_at(
                        source_data,
                        updated_at_field,
                    )

                    if source_timestamp is None:
                        raise ValueError(
                            f"Missing or invalid source timestamp: "
                            f"{updated_at_field}."
                        )

                mapped = _map_product_record(
                    source_data,
                    mappings,
                )

                sku = mapped["sku"]

                if sku in seen_skus:
                    raise ValueError(
                        f"Duplicate SKU '{sku}' found in source records."
                    )

                seen_skus.add(sku)

                with db.begin_nested():
                    result = _process_product_record(
                        db,
                        source_data,
                        mappings,
                        company_id,
                        user_id,
                        strategy,
                    )

                if result == "inserted":
                    inserted += 1

                elif result == "updated":
                    updated += 1

                elif result == "skipped":
                    skipped += 1

            except Exception as exc:
                failed += 1

                _record_sync_error(
                    db,
                    sync.id,
                    row_number,
                    source_data,
                    str(exc),
                )

        completed_at = _utc_now()

        duration_ms = int(
            (completed_at - sync.started_at).total_seconds() * 1000
        )

        if failed == 0:
            final_status = "completed"

        elif inserted or updated or skipped:
            final_status = "completed_with_errors"

        else:
            final_status = "failed"

        sync.status = final_status
        sync.processed_records = processed
        sync.inserted_records = inserted
        sync.updated_records = updated
        sync.skipped_records = skipped
        sync.failed_records = failed
        sync.completed_at = completed_at
        sync.duration_ms = duration_ms

        sync.error_summary = (
            f"{failed} record(s) failed."
            if failed
            else None
        )

        sync.execution_metadata = json.dumps({
            "duplicate_strategy": strategy,
            "target_module": integration.target_module,
            "source_type": integration.source_type,
            "trigger_type": trigger_type,
            "source_total_records": len(source_records),
            "selected_records": len(records),
            "previous_watermark": (
                previous_watermark.isoformat()
                if previous_watermark
                else None
            ),
        })

        integration.last_sync_at = completed_at
        integration.status = "active"

        if (
            failed == 0
            and updated_at_field
            and integration.source_type == "rest_api"
        ):
            latest_timestamp = _get_latest_source_timestamp(
                source_records,
                updated_at_field,
            )

            current_watermark = integration.last_source_sync_at

            if (
                current_watermark
                and current_watermark.tzinfo is None
            ):
                current_watermark = current_watermark.replace(
                    tzinfo=timezone.utc
                )

            if latest_timestamp:
                if (
                    current_watermark is None
                    or latest_timestamp > current_watermark
                ):
                    integration.last_source_sync_at = latest_timestamp

        _create_sync_audit(
            db=db,
            company_id=company_id,
            user_id=user_id,
            sync=sync,
            integration=integration,
            trigger_type=trigger_type,
            inserted=inserted,
            updated=updated,
            skipped=skipped,
            failed=failed,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.commit()
        db.refresh(sync)

        return {
            "message": "Product synchronization finished.",
            "sync_id": sync.id,
            "status": sync.status,
            "trigger_type": sync.trigger_type,
            "total_records": sync.total_records,
            "processed_records": sync.processed_records,
            "inserted_records": sync.inserted_records,
            "updated_records": sync.updated_records,
            "skipped_records": sync.skipped_records,
            "failed_records": sync.failed_records,
            "duration_ms": sync.duration_ms,
            "last_source_sync_at": (
                integration.last_source_sync_at.isoformat()
                if integration.last_source_sync_at
                else None
            ),
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Product synchronization failed unexpectedly.",
        )

def retry_failed_product_record(
    db: Session,
    integration_id: int,
    sync_id: int,
    error_id: int,
    company_id: int,
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
    corrected_source_data: dict = None,
):
    integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    if integration.source_type not in {"csv", "rest_api"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported integration source type.",
        )

    if integration.target_module != "products":
        raise HTTPException(
            status_code=400,
            detail="Product retry is currently supported only.",
        )

    if not integration.is_enabled:
        raise HTTPException(
            status_code=400,
            detail="Enable the integration before retrying.",
        )

    original_sync = (
        db.query(IntegrationSync)
        .filter(
            IntegrationSync.id == sync_id,
            IntegrationSync.integration_id == integration_id,
            IntegrationSync.company_id == company_id,
        )
        .first()
    )

    if not original_sync:
        raise HTTPException(
            status_code=404,
            detail="Original synchronization record not found.",
        )

    original_error = (
        db.query(IntegrationSyncError)
        .filter(
            IntegrationSyncError.id == error_id,
            IntegrationSyncError.sync_id == sync_id,
        )
        .with_for_update()
        .first()
    )

    if not original_error:
        raise HTTPException(
            status_code=404,
            detail="Failed record not found.",
        )

    if not original_error.is_retryable:
        raise HTTPException(
            status_code=400,
            detail="This failed record cannot be retried.",
        )

    if original_error.retry_status == "resolved":
        raise HTTPException(
            status_code=400,
            detail="This failed record has already been resolved.",
        )

    if original_error.retry_status == "processing":
        raise HTTPException(
            status_code=409,
            detail="This failed record is already being retried.",
        )

    source_data = (
        corrected_source_data
        if corrected_source_data is not None
        else original_error.source_data
    )

    if not isinstance(source_data, dict) or not source_data:
        raise HTTPException(
            status_code=400,
            detail="Original or corrected source record data is unavailable.",
        )

    if corrected_source_data is not None:
        original_error.source_data = source_data

    if not isinstance(source_data, dict) or not source_data:
        raise HTTPException(
            status_code=400,
            detail="Original source record data is unavailable.",
        )

    mappings = _get_mappings(
        db,
        integration_id,
    )

    if not mappings:
        raise HTTPException(
            status_code=400,
            detail="Configure field mappings before retrying.",
        )

    strategy = integration.sync_strategy

    if strategy not in {"insert", "update", "skip", "reject"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid duplicate handling strategy.",
        )

    retry_sync = IntegrationSync(
        integration_id=integration_id,
        company_id=company_id,
        triggered_by=user_id,
        trigger_type="retry",
        status="running",
        total_records=1,
        processed_records=0,
        inserted_records=0,
        updated_records=0,
        skipped_records=0,
        failed_records=0,
        started_at=_utc_now(),
    )

    original_error.retry_status = "processing"
    original_error.retry_count += 1
    original_error.last_retry_at = _utc_now()

    db.add(retry_sync)
    db.commit()
    db.refresh(retry_sync)

    inserted = 0
    updated = 0
    skipped = 0
    failed = 0
    error_message = None

    try:
        with db.begin_nested():
            result = _process_product_record(
                db,
                source_data,
                mappings,
                company_id,
                user_id,
                strategy,
            )

        if result == "inserted":
            inserted = 1

        elif result == "updated":
            updated = 1

        elif result == "skipped":
            skipped = 1

    except Exception as exc:
        failed = 1
        error_message = str(exc)

    completed_at = _utc_now()

    retry_sync.processed_records = 1
    retry_sync.inserted_records = inserted
    retry_sync.updated_records = updated
    retry_sync.skipped_records = skipped
    retry_sync.failed_records = failed
    retry_sync.completed_at = completed_at
    retry_sync.duration_ms = int(
        (completed_at - retry_sync.started_at).total_seconds() * 1000
    )

    if failed:
        retry_sync.status = "failed"
        retry_sync.error_summary = error_message

        original_error.retry_status = "failed"

        _record_sync_error(
            db,
            retry_sync.id,
            original_error.row_number,
            source_data,
            error_message,
        )

    else:
        retry_sync.status = "completed"
        original_error.retry_status = "resolved"
        original_error.resolved_at = completed_at

    retry_sync.execution_metadata = json.dumps({
        "duplicate_strategy": strategy,
        "target_module": integration.target_module,
        "source_type": integration.source_type,
        "original_sync_id": sync_id,
        "original_error_id": error_id,
    })

    integration.last_sync_at = completed_at
    integration.status = "active"

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Integration",
        action="UPDATE",
        resource_type="IntegrationSync",
        resource_id=str(retry_sync.id),
        description=(
            f"Failed product record retry finished. "
            f"SKU: {original_error.source_record_id}, "
            f"Status: {retry_sync.status}."
        ),
        after_values={
            "original_sync_id": sync_id,
            "original_error_id": error_id,
            "status": retry_sync.status,
            "inserted_records": inserted,
            "updated_records": updated,
            "skipped_records": skipped,
            "failed_records": failed,
        },
        ip_address=ip_address,
        user_agent=user_agent,
        status="SUCCESS" if not failed else "FAILED",
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save retry results.",
        )

    db.refresh(retry_sync)
    db.refresh(original_error)

    return {
        "message": (
            "Failed record retry completed."
            if not failed
            else "Failed record retry failed."
        ),
        "original_sync_id": sync_id,
        "error_id": error_id,
        "retry_sync_id": retry_sync.id,
        "status": retry_sync.status,
        "source_record_id": original_error.source_record_id,
        "retry_count": original_error.retry_count,
        "resolved": original_error.retry_status == "resolved",
        "inserted_records": inserted,
        "updated_records": updated,
        "skipped_records": skipped,
        "failed_records": failed,
        "error_message": error_message,
    }