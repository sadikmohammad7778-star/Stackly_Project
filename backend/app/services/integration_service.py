import csv
import uuid

from pathlib import Path
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.integration import Integration
from app.schemas.integration_schema import (
    IntegrationCreate,
    IntegrationUpdate,
)
from app.services.audit_service import create_audit_log
from app.models.integration_mapping import IntegrationMapping
from app.services.credential_encryption import encrypt_credentials
from app.services.integration_rest_service import fetch_rest_api_records

MAX_INTEGRATION_FILE_SIZE = 10 * 1024 * 1024

INTEGRATION_STORAGE = (
    Path(__file__).resolve().parents[2]
    / "storage"
    / "integrations"
)

def validate_connection_config(connection_config: dict):
    sensitive_keys = {
        "password",
        "passwd",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
        "client_secret",
        "authorization",
    }

    def check_values(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in sensitive_keys:
                    raise HTTPException(
                        status_code=400,
                        detail="Sensitive credentials must be provided separately."
                    )
                check_values(value)

        elif isinstance(data, list):
            for item in data:
                check_values(item)

    check_values(connection_config or {})


def create_integration(
    db: Session,
    integration: IntegrationCreate,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    try:
        existing = (
            db.query(Integration)
            .filter(
                Integration.company_id == company_id,
                Integration.name == integration.name,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="An integration with this name already exists.",
            )

        connection_config = integration.connection_config or {}
        validate_connection_config(connection_config)

        credentials = integration.credentials

        if credentials is not None and integration.source_type == "csv":
            raise HTTPException(
                status_code=400,
                detail="CSV integrations do not require credentials.",
            )

        encrypted_credentials = (
            encrypt_credentials(credentials)
            if credentials
            else None
        )

        db_integration = Integration(
            company_id=company_id,
            created_by=user_id,
            name=integration.name,
            source_type=integration.source_type,
            connection_config=connection_config,
            encrypted_credentials=encrypted_credentials,
            target_module=integration.target_module,
            sync_strategy=integration.sync_strategy,
            status="inactive",
            is_enabled=False,
        )

        db.add(db_integration)
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Integration",
            action="CREATE",
            resource_type="Integration",
            resource_id=str(db_integration.id),
            description=f"Created integration '{db_integration.name}'",
            after_values={
                "name": db_integration.name,
                "source_type": db_integration.source_type,
                "target_module": db_integration.target_module,
                "sync_strategy": db_integration.sync_strategy,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(db_integration)

        return db_integration

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create integration.",
        )

def get_all_integrations(
    db: Session,
    company_id: int,
):
    return (
        db.query(Integration)
        .filter(Integration.company_id == company_id)
        .order_by(Integration.id.desc())
        .all()
    )


def get_integration_by_id(
    db: Session,
    integration_id: int,
    company_id: int,
):
    integration = (
        db.query(Integration)
        .filter(
            Integration.id == integration_id,
            Integration.company_id == company_id,
        )
        .first()
    )

    if not integration:
        raise HTTPException(
            status_code=404,
            detail="Integration not found.",
        )

    return integration


def update_integration(
    db: Session,
    integration_id: int,
    integration: IntegrationUpdate,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    db_integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    try:
        before_values = {
            "name": db_integration.name,
            "source_type": db_integration.source_type,
            "target_module": db_integration.target_module,
            "sync_strategy": db_integration.sync_strategy,
            "is_enabled": db_integration.is_enabled,
        }

        update_data = integration.model_dump(exclude_unset=True)

        credentials = update_data.pop("credentials", None)

        if "connection_config" in update_data:
            validate_connection_config(
                update_data["connection_config"] or {}
            )

        if credentials is not None:
            if db_integration.source_type == "csv" and credentials:
                raise HTTPException(
                    status_code=400,
                    detail="CSV integrations do not require credentials.",
                )

            db_integration.encrypted_credentials = (
                encrypt_credentials(credentials)
                if credentials
                else None
            )

        if "name" in update_data:
            existing = (
                db.query(Integration)
                .filter(
                    Integration.company_id == company_id,
                    Integration.name == update_data["name"],
                    Integration.id != integration_id,
                )
                .first()
            )

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="An integration with this name already exists.",
                )

        for key, value in update_data.items():
            setattr(db_integration, key, value)

        after_values = {
            "name": db_integration.name,
            "source_type": db_integration.source_type,
            "target_module": db_integration.target_module,
            "sync_strategy": db_integration.sync_strategy,
            "is_enabled": db_integration.is_enabled,
        }

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Integration",
            action="UPDATE",
            resource_type="Integration",
            resource_id=str(db_integration.id),
            description=f"Updated integration '{db_integration.name}'",
            before_values=before_values,
            after_values=after_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(db_integration)

        return db_integration

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update integration.",
        )

def delete_integration(
    db: Session,
    integration_id: int,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    db_integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    try:
        integration_name = db_integration.name

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Integration",
            action="DELETE",
            resource_type="Integration",
            resource_id=str(integration_id),
            description=f"Deleted integration '{integration_name}'",
            before_values={
                "name": integration_name,
                "source_type": db_integration.source_type,
                "target_module": db_integration.target_module,
            },
            after_values=None,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.delete(db_integration)
        db.commit()

        return {
            "message": "Integration deleted successfully."
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete integration.",
        )


def _read_integration_csv(file_path: Path):
    try:
        with file_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file, strict=True)

            if not reader.fieldnames:
                raise HTTPException(
                    status_code=400,
                    detail="CSV file must contain column headers.",
                )

            columns = [
                column.strip()
                for column in reader.fieldnames
                if column is not None
            ]

            if len(columns) != len(reader.fieldnames):
                raise HTTPException(
                    status_code=400,
                    detail="CSV contains invalid column headers.",
                )

            if any(not column for column in columns):
                raise HTTPException(
                    status_code=400,
                    detail="CSV contains an empty column name.",
                )

            if len(columns) != len(set(columns)):
                raise HTTPException(
                    status_code=400,
                    detail="CSV contains duplicate column names.",
                )

            preview = []
            total_rows = 0

            for row in reader:
                if None in row:
                    raise HTTPException(
                        status_code=400,
                        detail="CSV contains rows with more values than headers.",
                    )

                if not any(
                    value and value.strip()
                    for value in row.values()
                    if value is not None
                ):
                    continue

                total_rows += 1

                if len(preview) < 5:
                    preview.append({
                        column: row.get(original_column)
                        for original_column, column in zip(
                            reader.fieldnames,
                            columns,
                        )
                    })

            return {
                "columns": columns,
                "total_rows": total_rows,
                "preview": preview,
            }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV must use UTF-8 encoding.",
        )

    except csv.Error:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file format.",
        )


def upload_integration_csv(
    db: Session,
    integration_id: int,
    company_id: int,
    user_id: int,
    upload: UploadFile,
    ip_address: str = None,
    user_agent: str = None,
):
    integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    if integration.source_type != "csv":
        raise HTTPException(
            status_code=400,
            detail="CSV upload is available only for CSV integrations.",
        )

    if not upload.filename or Path(upload.filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed.",
        )

    storage_directory = (
        INTEGRATION_STORAGE
        / f"company_{company_id}"
        / f"integration_{integration_id}"
    )

    storage_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated_filename = f"{uuid.uuid4().hex}.csv"

    final_path = storage_directory / generated_filename
    temporary_path = storage_directory / f"{generated_filename}.tmp"

    file_size = 0

    try:
        with temporary_path.open("wb") as destination:
            while True:
                chunk = upload.file.read(1024 * 1024)

                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > MAX_INTEGRATION_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="CSV file exceeds the 10 MB limit.",
                    )

                destination.write(chunk)

        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded CSV file is empty.",
            )

        csv_data = _read_integration_csv(temporary_path)

        final_path = temporary_path.with_suffix(".csv")
        temporary_path.replace(final_path)

        safe_filename = Path(upload.filename).name

        connection_config = dict(
            integration.connection_config or {}
        )

        previous_metadata = connection_config.get("csv_file")

        connection_config["csv_file"] = {
            "filename": safe_filename,
            "stored_filename": generated_filename,
            "storage_path": str(
                final_path.relative_to(INTEGRATION_STORAGE)
            ),
            "file_size": file_size,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

        integration.connection_config = connection_config
        integration.status = "configured"

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Integration",
            action="CREATE",
            resource_type="Integration",
            resource_id=str(integration.id),
            description=f"Uploaded CSV file for integration '{integration.name}'",
            after_values={
                "filename": safe_filename,
                "file_size": file_size,
                "total_rows": csv_data["total_rows"],
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(integration)

        if previous_metadata:
            old_relative_path = Path(
                previous_metadata.get("storage_path", "")
            )

            if (
                not old_relative_path.is_absolute()
                and ".." not in old_relative_path.parts
            ):
                old_path = (
                    INTEGRATION_STORAGE / old_relative_path
                ).resolve()

                storage_root = INTEGRATION_STORAGE.resolve()

                if (
                    old_path.is_relative_to(storage_root)
                    and old_path != final_path.resolve()
                    and old_path.is_file()
                ):
                    old_path.unlink()

        return {
            "integration_id": integration.id,
            "filename": safe_filename,
            "total_rows": csv_data["total_rows"],
            "columns": csv_data["columns"],
            "preview": csv_data["preview"],
            "message": "CSV uploaded and validated successfully.",
        }

    except HTTPException:
        db.rollback()

        if final_path.exists():
            final_path.unlink()

        if temporary_path.exists():
            temporary_path.unlink()

        raise

    except Exception:
        db.rollback()

        if final_path.exists():
            final_path.unlink()

        if temporary_path.exists():
            temporary_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Failed to upload integration CSV.",
        )


def preview_integration_csv(
    db: Session,
    integration_id: int,
    company_id: int,
):
    integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    csv_metadata = (
        integration.connection_config or {}
    ).get("csv_file")

    if not csv_metadata:
        raise HTTPException(
            status_code=404,
            detail="No CSV file has been uploaded for this integration.",
        )

    relative_path = Path(
        csv_metadata.get("storage_path", "")
    )

    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise HTTPException(
            status_code=400,
            detail="Invalid stored CSV path.",
        )

    storage_root = INTEGRATION_STORAGE.resolve()
    file_path = (storage_root / relative_path).resolve()

    if not file_path.is_relative_to(storage_root):
        raise HTTPException(
            status_code=400,
            detail="Invalid stored CSV path.",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stored CSV file was not found.",
        )

    csv_data = _read_integration_csv(file_path)

    return {
        "integration_id": integration.id,
        "filename": csv_metadata.get("filename"),
        "total_rows": csv_data["total_rows"],
        "columns": csv_data["columns"],
        "preview": csv_data["preview"],
    }


PRODUCT_MAPPING_FIELDS = {
    "sku": "string",
    "name": "string",
    "category_id": "integer",
    "brand": "string",
    "unit_price": "decimal",
    "stock_quantity": "integer",
    "description": "string",
    "status": "string",
    "is_active": "boolean",
}

PRODUCT_REQUIRED_MAPPING_FIELDS = {
    "sku",
    "name",
    "category_id",
    "unit_price",
    "stock_quantity",
}


def get_integration_source_fields(
    db: Session,
    integration: Integration,
):
    if integration.source_type == "csv":
        csv_metadata = (
            integration.connection_config or {}
        ).get("csv_file")

        if not csv_metadata:
            raise HTTPException(
                status_code=400,
                detail="Upload a CSV file before configuring mappings.",
            )

        relative_path = Path(
            csv_metadata.get("storage_path", "")
        )

        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise HTTPException(
                status_code=400,
                detail="Invalid stored CSV path.",
            )

        storage_root = INTEGRATION_STORAGE.resolve()
        file_path = (storage_root / relative_path).resolve()

        if not file_path.is_relative_to(storage_root):
            raise HTTPException(
                status_code=400,
                detail="Invalid stored CSV path.",
            )

        if not file_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Stored CSV file was not found.",
            )

        csv_data = _read_integration_csv(file_path)

        return csv_data["columns"]

    if integration.source_type == "rest_api":
        records = fetch_rest_api_records(integration)

        if not records:
            raise HTTPException(
                status_code=400,
                detail="REST API returned no records.",
            )

        return list(records[0].keys())

    raise HTTPException(
        status_code=400,
        detail="Field mapping is not supported for this source type.",
    )

def save_integration_mappings(
    db: Session,
    integration_id: int,
    company_id: int,
    user_id: int,
    mappings,
    ip_address: str = None,
    user_agent: str = None,
):
    integration = get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    if integration.source_type not in {"csv", "rest_api"}:
        raise HTTPException(
            status_code=400,
            detail="Field mapping is not supported for this source type.",
        )

    if integration.target_module != "products":
        raise HTTPException(
            status_code=400,
            detail="Product field mapping is currently supported only for products.",
        )

    available_fields = set(
        get_integration_source_fields(db, integration)
    )

    if not mappings:
        raise HTTPException(
            status_code=400,
            detail="At least one mapping is required.",
        )

    normalized_mappings = []

    for item in mappings:
        source_field = item.source_field.strip()
        target_field = item.target_field.strip()

        if source_field not in available_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Source field '{source_field}' does not exist.",
            )

        if target_field not in PRODUCT_MAPPING_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported product field '{target_field}'.",
            )

        normalized_mappings.append({
            "source_field": source_field,
            "target_field": target_field,
            "is_required": item.is_required,
            "transformation_config": item.transformation_config,
        })

    source_fields = [
        item["source_field"] for item in normalized_mappings
    ]

    target_fields = [
        item["target_field"] for item in normalized_mappings
    ]

    if len(source_fields) != len(set(source_fields)):
        raise HTTPException(
            status_code=400,
            detail="A source field cannot be mapped more than once.",
        )

    if len(target_fields) != len(set(target_fields)):
        raise HTTPException(
            status_code=400,
            detail="A product target field cannot be mapped more than once.",
        )

    missing_fields = (
        PRODUCT_REQUIRED_MAPPING_FIELDS - set(target_fields)
    )

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Required product mappings are missing.",
                "missing_fields": sorted(missing_fields),
            },
        )

    try:
        existing_mappings = (
            db.query(IntegrationMapping)
            .filter(
                IntegrationMapping.integration_id == integration_id
            )
            .all()
        )

        before_values = [
            {
                "source_field": mapping.source_field,
                "target_field": mapping.target_field,
            }
            for mapping in existing_mappings
        ]

        db.query(IntegrationMapping).filter(
            IntegrationMapping.integration_id == integration_id
        ).delete(synchronize_session=False)

        new_mappings = []

        for item in normalized_mappings:
            mapping = IntegrationMapping(
                integration_id=integration_id,
                source_field=item["source_field"],
                target_field=item["target_field"],
                source_type="string",
                target_type=PRODUCT_MAPPING_FIELDS[
                    item["target_field"]
                ],
                is_required=(
                    item["is_required"]
                    or item["target_field"]
                    in PRODUCT_REQUIRED_MAPPING_FIELDS
                ),
                is_active=True,
                transformation_config=item["transformation_config"],
            )

            db.add(mapping)
            new_mappings.append(mapping)

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Integration",
            action="UPDATE",
            resource_type="Integration",
            resource_id=str(integration_id),
            description=f"Updated mappings for integration '{integration.name}'",
            before_values={"mappings": before_values},
            after_values={
                "mappings": [
                    {
                        "source_field": item["source_field"],
                        "target_field": item["target_field"],
                    }
                    for item in normalized_mappings
                ]
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()

        for mapping in new_mappings:
            db.refresh(mapping)

        return new_mappings

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save integration mappings.",
        )    
def get_integration_mappings(
    db: Session,
    integration_id: int,
    company_id: int,
):
    get_integration_by_id(
        db,
        integration_id,
        company_id,
    )

    return (
        db.query(IntegrationMapping)
        .filter(
            IntegrationMapping.integration_id == integration_id,
            IntegrationMapping.is_active.is_(True),
        )
        .order_by(IntegrationMapping.id.asc())
        .all()
    )