from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem

from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.data_quality import DataQualityIssue, ReconciliationRun
from app.services.audit_service import create_audit_log
from app.schemas.report_schema import ReportFilters
from app.services.report_service import get_sales_report



class DataQualityService:

    @staticmethod
    def create_or_update_issue(
        db: Session,
        company_id: int,
        issue_type: str,
        severity: str,
        module: str,
        affected_record_type: str,
        affected_record_id: int,
        description: str,
        details: dict,
    ):
        issue_key = (
            f"{company_id}:"
            f"{issue_type}:"
            f"{affected_record_type}:"
            f"{affected_record_id}"
        )

        existing_issue = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.issue_key == issue_key,
            )
            .first()
        )

        if existing_issue:
            if existing_issue.status in ("OPEN", "INVESTIGATING"):
                existing_issue.severity = severity
                existing_issue.description = description
                existing_issue.details = details
                existing_issue.updated_at = datetime.utcnow()
                return existing_issue

            if existing_issue.status in ("RESOLVED", "IGNORED"):
                existing_issue.status = "OPEN"
                existing_issue.severity = severity
                existing_issue.description = description
                existing_issue.details = details
                existing_issue.resolved_at = None
                existing_issue.resolved_by = None
                existing_issue.resolution_note = None
                existing_issue.detected_at = datetime.utcnow()
                existing_issue.updated_at = datetime.utcnow()
                return existing_issue

        issue = DataQualityIssue(
            company_id=company_id,
            issue_type=issue_type,
            severity=severity,
            module=module,
            affected_record_type=affected_record_type,
            affected_record_id=affected_record_id,
            issue_key=issue_key,
            description=description,
            details=details,
            status="OPEN",
            detected_at=datetime.utcnow(),
        )

        db.add(issue)

        return issue

    @staticmethod
    def check_inventory_movements(
        db: Session,
        company_id: int,
    ):
        movements = (
            db.query(InventoryMovement)
            .join(
                Inventory,
                InventoryMovement.inventory_id == Inventory.id,
            )
            .filter(
                Inventory.company_id == company_id
            )
            .order_by(
                InventoryMovement.created_at.asc(),
                InventoryMovement.id.asc(),
            )
            .all()
        )

        issues = []

        for movement in movements:
            previous = movement.previous_quantity
            changed = movement.quantity_changed
            updated = movement.updated_quantity

            if movement.movement_type in (
                "IN",
                "Stock Addition",
            ):
                expected_quantity = previous + changed

            elif movement.movement_type in (
                "OUT",
                "Stock Removal",
            ):
                expected_quantity = previous - changed

            elif movement.movement_type == "Manual Adjustment":
                expected_quantity = changed

            else:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_STOCK_MOVEMENT",
                        severity="ERROR",
                        module="Inventory",
                        affected_record_type="InventoryMovement",
                        affected_record_id=movement.id,
                        description=(
                            f"Invalid inventory movement type: "
                            f"{movement.movement_type}"
                        ),
                        details={
                            "movement_id": movement.id,
                            "movement_type": movement.movement_type,
                            "previous_quantity": previous,
                            "quantity_changed": changed,
                            "updated_quantity": updated,
                        },
                    )
                )
                continue

            if expected_quantity != updated:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="STOCK_MOVEMENT_MISMATCH",
                        severity="ERROR",
                        module="Inventory",
                        affected_record_type="InventoryMovement",
                        affected_record_id=movement.id,
                        description=(
                            "Stock movement quantities are inconsistent."
                        ),
                        details={
                            "movement_id": movement.id,
                            "movement_type": movement.movement_type,
                            "previous_quantity": previous,
                            "quantity_changed": changed,
                            "expected_quantity": expected_quantity,
                            "updated_quantity": updated,
                            "difference": updated - expected_quantity,
                            "inventory_id": movement.inventory_id,
                        },
                    )
                )

        return issues

    @staticmethod
    def check_current_inventory(
        db: Session,
        company_id: int,
    ):
        inventories = (
            db.query(Inventory)
            .filter(
                Inventory.company_id == company_id
            )
            .all()
        )

        issues = []

        for inventory in inventories:
            latest_movement = (
                db.query(InventoryMovement)
                .filter(
                    InventoryMovement.inventory_id == inventory.id
                )
                .order_by(
                    InventoryMovement.created_at.desc(),
                    InventoryMovement.id.desc(),
                )
                .first()
            )

            if not latest_movement:
                continue

            expected_quantity = latest_movement.updated_quantity
            actual_quantity = inventory.current_stock

            if expected_quantity != actual_quantity:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVENTORY_MISMATCH",
                        severity="ERROR",
                        module="Inventory",
                        affected_record_type="Inventory",
                        affected_record_id=inventory.id,
                        description=(
                            "Current inventory quantity does not "
                            "match the latest stock movement."
                        ),
                        details={
                            "inventory_id": inventory.id,
                            "product_id": inventory.product_id,
                            "current_quantity": actual_quantity,
                            "expected_quantity": expected_quantity,
                            "difference": (
                                actual_quantity - expected_quantity
                            ),
                            "latest_movement_id": latest_movement.id,
                            "latest_movement_type": (
                                latest_movement.movement_type
                            ),
                        },
                    )
                )

        return issues


    @staticmethod
    def check_sales_data(db: Session, company_id: int):
        issues = []

        sales = (
            db.query(Sale)
            .filter(Sale.company_id == company_id)
            .all()
        )

        for sale in sales:
            if not sale.invoice_number:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="MISSING_SALE_DATA",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="Sale",
                        affected_record_id=sale.id,
                        description="Sale is missing invoice number.",
                        details={
                            "sale_id": sale.id
                        }
                    )
                )

            customer = (
                db.query(Customer)
                .filter(
                    Customer.id == sale.customer_id,
                    Customer.company_id == company_id
                )
                .first()
            )

            if not customer:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_SALE_CUSTOMER",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="Sale",
                        affected_record_id=sale.id,
                        description="Sale references an invalid customer.",
                        details={
                            "sale_id": sale.id,
                            "customer_id": sale.customer_id,
                            "invoice_number": sale.invoice_number
                        }
                    )
                )

            if sale.discount < 0 or sale.tax < 0 or sale.total_amount < 0:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_SALE_AMOUNT",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="Sale",
                        affected_record_id=sale.id,
                        description="Sale contains an invalid amount.",
                        details={
                            "sale_id": sale.id,
                            "discount": sale.discount,
                            "tax": sale.tax,
                            "total_amount": sale.total_amount
                        }
                    )
                )

            sale_items = (
                db.query(SaleItem)
                .filter(SaleItem.sale_id == sale.id)
                .all()
            )

            if not sale_items:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="SALE_WITHOUT_ITEMS",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="Sale",
                        affected_record_id=sale.id,
                        description="Sale does not contain any sale items.",
                        details={
                            "sale_id": sale.id,
                            "invoice_number": sale.invoice_number
                        }
                    )
                )
                continue

            calculated_total = 0

            for item in sale_items:
                if item.quantity <= 0:
                    issues.append(
                        DataQualityService.create_or_update_issue(
                            db=db,
                            company_id=company_id,
                            issue_type="INVALID_SALE_QUANTITY",
                            severity="ERROR",
                            module="Sales",
                            affected_record_type="SaleItem",
                            affected_record_id=item.id,
                            description="Sale item quantity must be greater than zero.",
                            details={
                                "sale_id": sale.id,
                                "sale_item_id": item.id,
                                "product_id": item.product_id,
                                "quantity": item.quantity
                            }
                        )
                    )

                product = (
                    db.query(Product)
                    .filter(
                        Product.id == item.product_id,
                        Product.company_id == company_id
                    )
                    .first()
                )

                if not product:
                    issues.append(
                        DataQualityService.create_or_update_issue(
                            db=db,
                            company_id=company_id,
                            issue_type="INVALID_SALE_PRODUCT",
                            severity="ERROR",
                            module="Sales",
                            affected_record_type="SaleItem",
                            affected_record_id=item.id,
                            description="Sale item references an invalid product.",
                            details={
                                "sale_id": sale.id,
                                "sale_item_id": item.id,
                                "product_id": item.product_id
                            }
                        )
                    )

                if (
                    item.unit_price < 0
                    or item.discount < 0
                    or item.tax < 0
                    or item.total < 0
                ):
                    issues.append(
                        DataQualityService.create_or_update_issue(
                            db=db,
                            company_id=company_id,
                            issue_type="INVALID_SALE_ITEM_AMOUNT",
                            severity="ERROR",
                            module="Sales",
                            affected_record_type="SaleItem",
                            affected_record_id=item.id,
                            description="Sale item contains an invalid amount.",
                            details={
                                "sale_id": sale.id,
                                "sale_item_id": item.id,
                                "unit_price": item.unit_price,
                                "discount": item.discount,
                                "tax": item.tax,
                                "total": item.total
                            }
                        )
                    )

                calculated_total += item.total

            calculated_total = round(
                calculated_total - sale.discount + sale.tax,
                2
            )

            actual_total = round(sale.total_amount, 2)

            if calculated_total != actual_total:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="SALE_TOTAL_MISMATCH",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="Sale",
                        affected_record_id=sale.id,
                        description="Sale total does not match sale item totals.",
                        details={
                            "sale_id": sale.id,
                            "invoice_number": sale.invoice_number,
                            "calculated_total": calculated_total,
                            "actual_total": actual_total,
                            "difference": round(
                                actual_total - calculated_total,
                                2
                            )
                        }
                    )
                )

        return issues


    @staticmethod
    def check_sale_stock_at_transaction_time(
        db: Session,
        company_id: int,
    ):
        issues = []

        sales = (
            db.query(Sale)
            .filter(Sale.company_id == company_id)
            .order_by(Sale.sale_date.asc(), Sale.id.asc())
            .all()
        )

        for sale in sales:
            sale_items = (
                db.query(SaleItem)
                .filter(SaleItem.sale_id == sale.id)
                .all()
            )

            for item in sale_items:
                inventory = (
                    db.query(Inventory)
                    .filter(
                        Inventory.product_id == item.product_id,
                        Inventory.company_id == company_id,
                    )
                    .first()
                )

                if not inventory:
                    continue

                movements = (
                    db.query(InventoryMovement)
                    .filter(
                        InventoryMovement.inventory_id == inventory.id,
                        InventoryMovement.created_at <= sale.sale_date,
                    )
                    .order_by(
                        InventoryMovement.created_at.asc(),
                        InventoryMovement.id.asc(),
                    )
                    .all()
                )

                if not movements:
                    continue

                stock_at_sale = movements[-1].updated_quantity

                if item.quantity > stock_at_sale:
                    issues.append(
                        DataQualityService.create_or_update_issue(
                            db=db,
                            company_id=company_id,
                            issue_type="SALE_QUANTITY_EXCEEDS_STOCK",
                            severity="ERROR",
                            module="Sales",
                            affected_record_type="SaleItem",
                            affected_record_id=item.id,
                            description=(
                                "Sale quantity exceeds available stock "
                                "at the transaction time."
                            ),
                            details={
                                "sale_id": sale.id,
                                "sale_item_id": item.id,
                                "invoice_number": sale.invoice_number,
                                "product_id": item.product_id,
                                "sale_date": sale.sale_date.isoformat(),
                                "sale_quantity": item.quantity,
                                "stock_at_transaction": stock_at_sale,
                                "difference": item.quantity - stock_at_sale,
                                "inventory_id": inventory.id,
                            },
                        )
                    )

        return issues

    @staticmethod
    def check_sale_invoice_data(
        db: Session,
        company_id: int,
    ):
        issues = []

        duplicate_invoices = (
            db.query(
                Sale.invoice_number,
                func.count(Sale.id).label("invoice_count"),
            )
            .filter(
                Sale.company_id == company_id,
                Sale.invoice_number.isnot(None),
            )
            .group_by(Sale.invoice_number)
            .having(func.count(Sale.id) > 1)
            .all()
        )

        for invoice_number, invoice_count in duplicate_invoices:
            sales = (
                db.query(Sale)
                .filter(
                    Sale.company_id == company_id,
                    Sale.invoice_number == invoice_number,
                )
                .all()
            )

            for sale in sales:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="DUPLICATE_INVOICE_NUMBER",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="Sale",
                        affected_record_id=sale.id,
                        description=(
                            f"Duplicate invoice number detected: "
                            f"{invoice_number}"
                        ),
                        details={
                            "sale_id": sale.id,
                            "invoice_number": invoice_number,
                            "duplicate_count": invoice_count,
                        },
                    )
                )

        sales = (
            db.query(Sale)
            .filter(Sale.company_id == company_id)
            .all()
        )

        for sale in sales:
            missing_fields = []

            if not sale.invoice_number or not sale.invoice_number.strip():
                missing_fields.append("invoice_number")

            if not sale.customer_id:
                missing_fields.append("customer_id")

            if not sale.sales_channel or not sale.sales_channel.strip():
                missing_fields.append("sales_channel")

            if not sale.payment_method or not sale.payment_method.strip():
                missing_fields.append("payment_method")

            if sale.sale_date is None:
                missing_fields.append("sale_date")

            if missing_fields:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="MISSING_SALE_DATA",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="Sale",
                        affected_record_id=sale.id,
                        description="Sale is missing mandatory data.",
                        details={
                            "sale_id": sale.id,
                            "invoice_number": sale.invoice_number,
                            "missing_fields": missing_fields,
                        },
                    )
                )

        return issues
    
    @staticmethod
    def run_inventory_reconciliation(
        db: Session,
        company_id: int,
        triggered_by: int = None,
    ):
        reconciliation_run = ReconciliationRun(
            company_id=company_id,
            triggered_by=triggered_by,
            started_at=datetime.utcnow(),
            execution_status="RUNNING",
            records_checked=0,
            issues_detected=0,
            issues_resolved=0,
            failed_checks=0,
        )

        db.add(reconciliation_run)
        db.flush()

        try:
            movement_issues = (
                DataQualityService.check_inventory_movements(
                    db,
                    company_id,
                )
            )

            product_issues = (
                DataQualityService.check_product_data(
                    db,
                    company_id,
                )
            )

            customer_issues = (
                DataQualityService.check_customer_data(
                    db,
                    company_id,
                )
            )

            sales_issues = DataQualityService.check_sales_data(
                db,
                company_id
            )

            sale_stock_issues = (
                DataQualityService.check_sale_stock_at_transaction_time(
                    db,
                    company_id,
                )
            )

            sale_invoice_issues = (
                DataQualityService.check_sale_invoice_data(
                    db,
                    company_id,
                )
            )

            report_issues = DataQualityService.check_report_totals(
                db,
                company_id,
            )

            inventory_issues = (
                DataQualityService.check_current_inventory(
                    db,
                    company_id,
                )
            )

            issues = (
                movement_issues
                + inventory_issues
                + product_issues
                + customer_issues
                + sales_issues
                + sale_stock_issues
                +sale_invoice_issues
                +report_issues
            )

            detected_issue_keys = {
                issue.issue_key
                for issue in issues
            }

            existing_issues = (
                db.query(DataQualityIssue)
                .filter(
                    DataQualityIssue.company_id == company_id,
                    DataQualityIssue.module.in_(
                        ["Inventory", "Product","Customer","Sales","Reports"]
                    ),
                    DataQualityIssue.status.in_(
                        ["OPEN", "INVESTIGATING"]
                    ),
                )
                .all()
            )

            resolved_count = 0

            for existing_issue in existing_issues:
                if existing_issue.issue_key not in detected_issue_keys:
                    existing_issue.status = "RESOLVED"
                    existing_issue.resolved_at = datetime.utcnow()
                    existing_issue.resolved_by = None
                    existing_issue.resolution_note = (
                        "Issue no longer detected during reconciliation."
                    )
                    existing_issue.updated_at = datetime.utcnow()
                    resolved_count += 1

            inventory_count = (
                db.query(Inventory)
                .filter(
                    Inventory.company_id == company_id
                )
                .count()
            )

            movement_count = (
                db.query(InventoryMovement)
                .join(
                    Inventory,
                    InventoryMovement.inventory_id == Inventory.id,
                )
                .filter(
                    Inventory.company_id == company_id
                )
                .count()
            )

            product_count = (
                db.query(Product)
                .filter(
                    Product.company_id == company_id
                )
                .count()
            )

            customer_count = (
                db.query(Customer)
                .filter(
                    Customer.company_id == company_id
                )
                .count()
            )

            sales_count = (
                db.query(Sale)
                .filter(Sale.company_id == company_id)
                .count()
            )

            sale_item_count = (
                db.query(SaleItem)
                .join(Sale, Sale.id == SaleItem.sale_id)
                .filter(Sale.company_id == company_id)
                .count()
            )

            records_checked = (
                inventory_count
                + movement_count
                + product_count
                + customer_count
                +sales_count
                +sale_item_count
            )
            reconciliation_run.records_checked = records_checked
            reconciliation_run.issues_detected = len(issues)
            reconciliation_run.issues_resolved = resolved_count
            reconciliation_run.failed_checks = 0
            reconciliation_run.execution_status = "COMPLETED"
            reconciliation_run.completed_at = datetime.utcnow()

            db.commit()

            issue_data = []

            for issue in issues:
                issue_data.append({
                    "id": issue.id,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "module": issue.module,
                    "affected_record_type": issue.affected_record_type,
                    "affected_record_id": issue.affected_record_id,
                    "description": issue.description,
                    "details": issue.details,
                    "status": issue.status,
                    "detected_at": issue.detected_at,
                })

            return {
                "run_id": reconciliation_run.id,
                "records_checked": records_checked,
                "issues_detected": len(issues),
                "issues_resolved": resolved_count,
                "failed_checks": 0,
                "execution_status": "COMPLETED",
                "issues": issue_data,
            }

        except Exception as exc:
            reconciliation_run.execution_status = "FAILED"
            reconciliation_run.error_message = str(exc)
            reconciliation_run.completed_at = datetime.utcnow()

            db.commit()

            raise


    @staticmethod
    def get_reconciliation_history(
        db: Session,
        company_id: int,
    ):
        runs = (
            db.query(ReconciliationRun)
            .filter(
                ReconciliationRun.company_id == company_id
            )
            .order_by(
                ReconciliationRun.started_at.desc(),
                ReconciliationRun.id.desc(),
            )
            .all()
        )

        return [
            {
                "id": run.id,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
                "triggered_by": run.triggered_by,
                "records_checked": run.records_checked,
                "issues_detected": run.issues_detected,
                "issues_resolved": run.issues_resolved,
                "failed_checks": run.failed_checks,
                "execution_status": run.execution_status,
                "error_message": run.error_message,
            }
            for run in runs
        ]    


    @staticmethod
    def get_data_quality_issues(
        db: Session,
        company_id: int,
        status: str = None,
        severity: str = None,
        issue_type: str = None,
        module: str = None,
        search: str = None,
    ):
        query = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.company_id == company_id
            )
        )

        if status:
            query = query.filter(
                DataQualityIssue.status == status.upper()
            )

        if severity:
            query = query.filter(
                DataQualityIssue.severity == severity.upper()
            )

        if issue_type:
            query = query.filter(
                DataQualityIssue.issue_type == issue_type
            )

        if module:
            query = query.filter(
                DataQualityIssue.module == module
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                DataQualityIssue.description.ilike(search_value)
                | DataQualityIssue.issue_type.ilike(search_value)
                | DataQualityIssue.module.ilike(search_value)
                | DataQualityIssue.affected_record_type.ilike(
                    search_value
                )
            )

        issues = (
            query
            .order_by(
                DataQualityIssue.detected_at.desc(),
                DataQualityIssue.id.desc(),
            )
            .all()
        )

        return [
            {
                "id": issue.id,
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "module": issue.module,
                "affected_record_type": issue.affected_record_type,
                "affected_record_id": issue.affected_record_id,
                "description": issue.description,
                "details": issue.details,
                "status": issue.status,
                "detected_at": issue.detected_at,
                "resolved_at": issue.resolved_at,
                "resolved_by": issue.resolved_by,
                "resolution_note": issue.resolution_note,
                "created_at": issue.created_at,
                "updated_at": issue.updated_at,
            }
            for issue in issues
        ]


    @staticmethod
    def get_data_quality_issue(
        db: Session,
        company_id: int,
        issue_id: int,
    ):
        issue = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.id == issue_id,
                DataQualityIssue.company_id == company_id,
            )
            .first()
        )

        if not issue:
            return {
                "message": "Data quality issue not found."
            }

        return {
            "id": issue.id,
            "issue_type": issue.issue_type,
            "severity": issue.severity,
            "module": issue.module,
            "affected_record_type": issue.affected_record_type,
            "affected_record_id": issue.affected_record_id,
            "description": issue.description,
            "details": issue.details,
            "status": issue.status,
            "detected_at": issue.detected_at,
            "resolved_at": issue.resolved_at,
            "resolved_by": issue.resolved_by,
            "resolution_note": issue.resolution_note,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
        }

    @staticmethod
    def update_data_quality_issue(
        db: Session,
        company_id: int,
        issue_id: int,
        status: str,
        resolution_note: str = None,
        resolved_by: int = None,
    ):
        allowed_statuses = {
            "OPEN",
            "INVESTIGATING",
            "RESOLVED",
            "IGNORED",
        }

        if status not in allowed_statuses:
            raise ValueError("Invalid data quality issue status.")

        issue = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.id == issue_id,
                DataQualityIssue.company_id == company_id,
            )
            .first()
        )

        if not issue:
            raise ValueError("Data quality issue not found.")

        old_status = issue.status
        old_resolution_note = issue.resolution_note

        issue.status = status
        issue.resolution_note = resolution_note

        if status in {"RESOLVED", "IGNORED"}:
            issue.resolved_at = datetime.utcnow()
            issue.resolved_by = resolved_by
        else:
            issue.resolved_at = None
            issue.resolved_by = None

        issue.updated_at = datetime.utcnow()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=resolved_by,
            module="Data Quality",
            action="UPDATE",
            description=f"Data quality issue {issue_id} status changed from {old_status} to {status}.",
            resource_type="DataQualityIssue",
            resource_id=str(issue_id),
            before_values={
                "status": old_status,
                "resolution_note": old_resolution_note,
            },
            after_values={
                "status": status,
                "resolution_note": resolution_note,
            },
        )

        db.commit()
        db.refresh(issue)

        return {
            "id": issue.id,
            "issue_type": issue.issue_type,
            "severity": issue.severity,
            "module": issue.module,
            "affected_record_type": issue.affected_record_type,
            "affected_record_id": issue.affected_record_id,
            "description": issue.description,
            "details": issue.details,
            "status": issue.status,
            "detected_at": issue.detected_at,
            "resolved_at": issue.resolved_at,
            "resolved_by": issue.resolved_by,
            "resolution_note": issue.resolution_note,
        }


    @staticmethod
    def get_data_quality_dashboard(
        db: Session,
        company_id: int,
    ):
        total_inventory = (
            db.query(Inventory)
            .filter(
                Inventory.company_id == company_id
            )
            .count()
        )

        total_movements = (
            db.query(InventoryMovement)
            .join(
                Inventory,
                InventoryMovement.inventory_id == Inventory.id,
            )
            .filter(
                Inventory.company_id == company_id
            )
            .count()
        )

        total_products = (
            db.query(Product)
            .filter(
                Product.company_id == company_id
            )
            .count()
        )

        total_customers = (
            db.query(Customer)
            .filter(
                Customer.company_id == company_id
            )
            .count()
        )

        total_sales = (
            db.query(Sale)
            .filter(
                Sale.company_id == company_id
            )
            .count()
        )

        total_sale_items = (
            db.query(SaleItem)
            .join(
                Sale,
                Sale.id == SaleItem.sale_id,
            )
            .filter(
                Sale.company_id == company_id
            )
            .count()
        )

        total_checked = (
            total_inventory
            + total_movements
            + total_products
            + total_customers
            + total_sales
            + total_sale_items
        )

        total_issues = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.company_id == company_id
            )
            .count()
        )

        open_issues = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.status.in_(
                    ["OPEN", "INVESTIGATING"]
                ),
            )
            .count()
        )

        resolved_issues = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.status == "RESOLVED",
            )
            .count()
        )

        ignored_issues = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.status == "IGNORED",
            )
            .count()
        )

        error_issues = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.severity == "ERROR",
                DataQualityIssue.status.in_(
                    ["OPEN", "INVESTIGATING"]
                ),
            )
            .count()
        )

        warning_issues = (
            db.query(DataQualityIssue)
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.severity == "WARNING",
                DataQualityIssue.status.in_(
                    ["OPEN", "INVESTIGATING"]
                ),
            )
            .count()
        )

        last_run = (
            db.query(ReconciliationRun)
            .filter(
                ReconciliationRun.company_id == company_id
            )
            .order_by(
                ReconciliationRun.started_at.desc(),
                ReconciliationRun.id.desc(),
            )
            .first()
        )

        issue_type_rows = (
            db.query(
                DataQualityIssue.issue_type,
                DataQualityIssue.id,
            )
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.status.in_(
                    ["OPEN", "INVESTIGATING"]
                ),
            )
            .all()
        )

        issues_by_type = {}

        for issue_type, issue_id in issue_type_rows:
            issues_by_type[issue_type] = (
                issues_by_type.get(issue_type, 0) + 1
            )

        module_rows = (
            db.query(
                DataQualityIssue.module,
                DataQualityIssue.id,
            )
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.status.in_(
                    ["OPEN", "INVESTIGATING"]
                ),
            )
            .all()
        )

        issues_by_module = {}

        for module, issue_id in module_rows:
            issues_by_module[module] = (
                issues_by_module.get(module, 0) + 1
            )

        severity_rows = (
            db.query(
                DataQualityIssue.severity,
                DataQualityIssue.id,
            )
            .filter(
                DataQualityIssue.company_id == company_id,
                DataQualityIssue.status.in_(
                    ["OPEN", "INVESTIGATING"]
                ),
            )
            .all()
        )

        issues_by_severity = {}

        for severity, issue_id in severity_rows:
            issues_by_severity[severity] = (
                issues_by_severity.get(severity, 0) + 1
            )

        issues_by_severity = {}

        for severity, issue_id in severity_rows:
            issues_by_severity[severity] = (
                issues_by_severity.get(severity, 0) + 1
            )

        valid_records = max(
            total_checked - open_issues,
            0,
        )

        return {
            "total_checked": total_checked,
            "valid_records": valid_records,
            "total_issues": total_issues,
            "open_issues": open_issues,
            "resolved_issues": resolved_issues,
            "ignored_issues": ignored_issues,
            "errors": error_issues,
            "warnings": warning_issues,
            "last_reconciliation": (
                {
                    "id": last_run.id,
                    "started_at": last_run.started_at,
                    "completed_at": last_run.completed_at,
                    "records_checked": last_run.records_checked,
                    "issues_detected": last_run.issues_detected,
                    "issues_resolved": last_run.issues_resolved,
                    "execution_status": last_run.execution_status,
                }
                if last_run
                else None
            ),
            "issues_by_severity": issues_by_severity,
            "issues_by_type": issues_by_type,
            "issues_by_module": issues_by_module,
        }

    @staticmethod
    def check_product_data(
        db: Session,
        company_id: int,
    ):
        issues = []

        duplicate_skus = (
            db.query(
                Product.sku,
                func.count(Product.id).label("sku_count"),
            )
            .filter(
                Product.company_id == company_id,
                Product.sku.isnot(None),
            )
            .group_by(Product.sku)
            .having(func.count(Product.id) > 1)
            .all()
        )

        for sku, sku_count in duplicate_skus:
            products = (
                db.query(Product)
                .filter(
                    Product.company_id == company_id,
                    Product.sku == sku,
                )
                .all()
            )

            for product in products:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="DUPLICATE_SKU",
                        severity="ERROR",
                        module="Product",
                        affected_record_type="Product",
                        affected_record_id=product.id,
                        description=(
                            f"Duplicate SKU detected: {sku}"
                        ),
                        details={
                            "product_id": product.id,
                            "sku": sku,
                            "duplicate_count": sku_count,
                        },
                    )
                )

        products = (
            db.query(Product)
            .filter(
                Product.company_id == company_id
            )
            .all()
        )

        for product in products:
            sku = product.sku.strip() if product.sku else ""

            if not sku:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_SKU",
                        severity="ERROR",
                        module="Product",
                        affected_record_type="Product",
                        affected_record_id=product.id,
                        description="Product SKU is missing or empty.",
                        details={
                            "product_id": product.id,
                            "sku": product.sku,
                        },
                    )
                )

            elif len(sku) > 100:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_SKU",
                        severity="ERROR",
                        module="Product",
                        affected_record_type="Product",
                        affected_record_id=product.id,
                        description="Product SKU exceeds the maximum length.",
                        details={
                            "product_id": product.id,
                            "sku": sku,
                            "length": len(sku),
                            "maximum_length": 100,
                        },
                    )
                )

            missing_fields = []

            if not product.name or not product.name.strip():
                missing_fields.append("name")

            if not product.brand or not product.brand.strip():
                missing_fields.append("brand")

            if product.category_id is None:
                missing_fields.append("category_id")

            if product.unit_price is None:
                missing_fields.append("unit_price")

            if missing_fields:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="MISSING_PRODUCT_DATA",
                        severity="ERROR",
                        module="Product",
                        affected_record_type="Product",
                        affected_record_id=product.id,
                        description=(
                            "Product is missing mandatory data."
                        ),
                        details={
                            "product_id": product.id,
                            "missing_fields": missing_fields,
                        },
                    )
                )

            if not product.is_active:
                inventory = (
                    db.query(Inventory)
                    .filter(
                        Inventory.product_id == product.id,
                        Inventory.company_id == company_id,
                    )
                    .first()
                )

                if inventory and (
                    inventory.current_stock > 0
                    or inventory.available_stock > 0
                ):
                    issues.append(
                        DataQualityService.create_or_update_issue(
                            db=db,
                            company_id=company_id,
                            issue_type="INACTIVE_PRODUCT_WITH_STOCK",
                            severity="WARNING",
                            module="Product",
                            affected_record_type="Product",
                            affected_record_id=product.id,
                            description=(
                                "Inactive product has available inventory."
                            ),
                            details={
                                "product_id": product.id,
                                "sku": product.sku,
                                "product_name": product.name,
                                "current_stock": inventory.current_stock,
                                "available_stock": inventory.available_stock,
                            },
                        )
                    )

        return issues


    @staticmethod
    def check_customer_data(
        db: Session,
        company_id: int,
    ):
        issues = []

        duplicate_customer_ids = (
            db.query(
                Customer.customer_id,
                func.count(Customer.id).label("customer_count"),
            )
            .filter(
                Customer.company_id == company_id,
                Customer.customer_id.isnot(None),
            )
            .group_by(Customer.customer_id)
            .having(func.count(Customer.id) > 1)
            .all()
        )

        for customer_id, customer_count in duplicate_customer_ids:
            customers = (
                db.query(Customer)
                .filter(
                    Customer.company_id == company_id,
                    Customer.customer_id == customer_id,
                )
                .all()
            )

            for customer in customers:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="DUPLICATE_CUSTOMER_ID",
                        severity="ERROR",
                        module="Customer",
                        affected_record_type="Customer",
                        affected_record_id=customer.id,
                        description=(
                            f"Duplicate customer ID detected: "
                            f"{customer_id}"
                        ),
                        details={
                            "customer_id": customer_id,
                            "customer_count": customer_count,
                        },
                    )
                )

        duplicate_emails = (
            db.query(
                Customer.email,
                func.count(Customer.id).label("customer_count"),
            )
            .filter(
                Customer.company_id == company_id,
                Customer.email.isnot(None),
            )
            .group_by(Customer.email)
            .having(func.count(Customer.id) > 1)
            .all()
        )

        for email, customer_count in duplicate_emails:
            customers = (
                db.query(Customer)
                .filter(
                    Customer.company_id == company_id,
                    Customer.email == email,
                )
                .all()
            )

            for customer in customers:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="DUPLICATE_CUSTOMER_EMAIL",
                        severity="ERROR",
                        module="Customer",
                        affected_record_type="Customer",
                        affected_record_id=customer.id,
                        description=(
                            f"Duplicate customer email detected: "
                            f"{email}"
                        ),
                        details={
                            "customer_id": customer.customer_id,
                            "email": email,
                            "customer_count": customer_count,
                        },
                    )
                )

        duplicate_phones = (
            db.query(
                Customer.phone,
                func.count(Customer.id).label("customer_count"),
            )
            .filter(
                Customer.company_id == company_id,
                Customer.phone.isnot(None),
            )
            .group_by(Customer.phone)
            .having(func.count(Customer.id) > 1)
            .all()
        )

        for phone, customer_count in duplicate_phones:
            customers = (
                db.query(Customer)
                .filter(
                    Customer.company_id == company_id,
                    Customer.phone == phone,
                )
                .all()
            )

            for customer in customers:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="DUPLICATE_CUSTOMER_PHONE",
                        severity="ERROR",
                        module="Customer",
                        affected_record_type="Customer",
                        affected_record_id=customer.id,
                        description=(
                            f"Duplicate customer phone detected: "
                            f"{phone}"
                        ),
                        details={
                            "customer_id": customer.customer_id,
                            "phone": phone,
                            "customer_count": customer_count,
                        },
                    )
                )

        customers = (
            db.query(Customer)
            .filter(
                Customer.company_id == company_id
            )
            .all()
        )

        valid_statuses = {
            "Active",
            "Inactive",
        }

        for customer in customers:
            customer_id = (
                customer.customer_id.strip()
                if customer.customer_id
                else ""
            )

            missing_fields = []

            if not customer_id:
                missing_fields.append("customer_id")

            if not customer.first_name or not customer.first_name.strip():
                missing_fields.append("first_name")

            if not customer.last_name or not customer.last_name.strip():
                missing_fields.append("last_name")

            if not customer.email or not customer.email.strip():
                missing_fields.append("email")

            if not customer.phone or not customer.phone.strip():
                missing_fields.append("phone")

            if not customer.address or not customer.address.strip():
                missing_fields.append("address")

            if not customer.city or not customer.city.strip():
                missing_fields.append("city")

            if not customer.state or not customer.state.strip():
                missing_fields.append("state")

            if not customer.country or not customer.country.strip():
                missing_fields.append("country")

            if not customer.postal_code or not customer.postal_code.strip():
                missing_fields.append("postal_code")

            if missing_fields:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="MISSING_CUSTOMER_DATA",
                        severity="ERROR",
                        module="Customer",
                        affected_record_type="Customer",
                        affected_record_id=customer.id,
                        description=(
                            "Customer is missing mandatory data."
                        ),
                        details={
                            "customer_id": customer.customer_id,
                            "missing_fields": missing_fields,
                        },
                    )
                )

            if customer.customer_id and len(customer_id) > 20:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_CUSTOMER_ID",
                        severity="ERROR",
                        module="Customer",
                        affected_record_type="Customer",
                        affected_record_id=customer.id,
                        description=(
                            "Customer ID exceeds the maximum length."
                        ),
                        details={
                            "customer_id": customer.customer_id,
                            "length": len(customer_id),
                            "maximum_length": 20,
                        },
                    )
                )

            if customer.email:
                email = customer.email.strip()

                if "@" not in email or "." not in email.split("@")[-1]:
                    issues.append(
                        DataQualityService.create_or_update_issue(
                            db=db,
                            company_id=company_id,
                            issue_type="INVALID_CUSTOMER_EMAIL",
                            severity="ERROR",
                            module="Customer",
                            affected_record_type="Customer",
                            affected_record_id=customer.id,
                            description=(
                                "Customer email format is invalid."
                            ),
                            details={
                                "customer_id": customer.customer_id,
                                "email": customer.email,
                            },
                        )
                    )

            if customer.status not in valid_statuses:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_CUSTOMER_STATUS",
                        severity="ERROR",
                        module="Customer",
                        affected_record_type="Customer",
                        affected_record_id=customer.id,
                        description=(
                            "Customer has an invalid status."
                        ),
                        details={
                            "customer_id": customer.customer_id,
                            "status": customer.status,
                            "allowed_statuses": list(valid_statuses),
                        },
                    )
                )

            if customer.deleted_at is not None and customer.status == "Active":
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="DELETED_ACTIVE_CUSTOMER",
                        severity="WARNING",
                        module="Customer",
                        affected_record_type="Customer",
                        affected_record_id=customer.id,
                        description=(
                            "Deleted customer is still marked as Active."
                        ),
                        details={
                            "customer_id": customer.customer_id,
                            "deleted_at": customer.deleted_at.isoformat(),
                            "status": customer.status,
                        },
                    )
                )

        return issues


    @staticmethod
    def check_report_totals(
        db: Session,
        company_id: int,
    ):
        issues = []

        report = get_sales_report(
            db=db,
            company_id=company_id,
        )

        direct_sales_count = (
            db.query(Sale)
            .filter(
                Sale.company_id == company_id
            )
            .count()
        )

        direct_revenue = (
            db.query(
                func.coalesce(
                    func.sum(Sale.total_amount),
                    0,
                )
            )
            .filter(
                Sale.company_id == company_id
            )
            .scalar()
            or 0
        )

        direct_revenue = float(direct_revenue)

        direct_average_order_value = (
            direct_revenue / direct_sales_count
            if direct_sales_count > 0
            else 0
        )

        report_total_sales = int(
            report.total_sales or 0
        )

        report_total_revenue = float(
            report.total_revenue or 0
        )

        report_average_order_value = float(
            report.average_order_value or 0
        )

        mismatches = []

        if report_total_sales != direct_sales_count:
            mismatches.append({
                "field": "total_sales",
                "report_value": report_total_sales,
                "source_value": direct_sales_count,
            })

        if abs(report_total_revenue - direct_revenue) > 0.01:
            mismatches.append({
                "field": "total_revenue",
                "report_value": report_total_revenue,
                "source_value": direct_revenue,
            })

        if abs(
            report_average_order_value
            - direct_average_order_value
        ) > 0.01:
            mismatches.append({
                "field": "average_order_value",
                "report_value": report_average_order_value,
                "source_value": direct_average_order_value,
            })

        if mismatches:
            issue = DataQualityService.create_or_update_issue(
                db=db,
                company_id=company_id,
                issue_type="REPORT_TOTAL_MISMATCH",
                severity="ERROR",
                module="Reports",
                affected_record_type="SalesReport",
                affected_record_id=None,
                description="Sales report totals do not match the underlying sales data.",
                details={
                    "mismatches": mismatches,
                    "report": {
                        "total_sales": report_total_sales,
                        "total_revenue": report_total_revenue,
                        "average_order_value": report_average_order_value,
                    },
                    "source": {
                        "total_sales": direct_sales_count,
                        "total_revenue": direct_revenue,
                        "average_order_value": direct_average_order_value,
                    },
                },
            )

            issues.append(issue)

        return issues



    @staticmethod
    def run_product_lightweight_check(
        db: Session,
        company_id: int,
        product_id: int,
    ):
        product = (
            db.query(Product)
            .filter(
                Product.id == product_id,
                Product.company_id == company_id,
            )
            .first()
        )

        if not product:
            return []

        issues = []

        if not product.sku or not product.sku.strip():
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="INVALID_SKU",
                    severity="ERROR",
                    module="Product",
                    affected_record_type="Product",
                    affected_record_id=product.id,
                    description="Product SKU is missing.",
                    details={
                        "product_id": product.id,
                        "sku": product.sku,
                    },
                )
            )

        if (
            not product.name
            or not product.brand
            or not product.category_id
            or product.unit_price is None
            or product.unit_price <= 0
        ):
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="MISSING_PRODUCT_DATA",
                    severity="ERROR",
                    module="Product",
                    affected_record_type="Product",
                    affected_record_id=product.id,
                    description="Product contains missing or invalid mandatory data.",
                    details={
                        "product_id": product.id,
                        "name": product.name,
                        "brand": product.brand,
                        "category_id": product.category_id,
                        "unit_price": product.unit_price,
                    },
                )
            )

        if not product.is_active and (product.stock_quantity or 0) > 0:
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="INACTIVE_PRODUCT_WITH_STOCK",
                    severity="WARNING",
                    module="Product",
                    affected_record_type="Product",
                    affected_record_id=product.id,
                    description="Inactive product has available stock.",
                    details={
                        "product_id": product.id,
                        "stock_quantity": product.stock_quantity,
                        "is_active": product.is_active,
                    },
                )
            )

        db.flush()

        return issues


    @staticmethod
    def run_customer_lightweight_check(
        db: Session,
        company_id: int,
        customer_id: int,
    ):
        customer = (
            db.query(Customer)
            .filter(
                Customer.id == customer_id,
                Customer.company_id == company_id,
            )
            .first()
        )

        if not customer:
            return []

        issues = []

        mandatory_fields = {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "city": customer.city,
            "state": customer.state,
            "country": customer.country,
            "postal_code": customer.postal_code,
        }

        missing_fields = [
            field
            for field, value in mandatory_fields.items()
            if value is None or not str(value).strip()
        ]

        if missing_fields:
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="MISSING_CUSTOMER_DATA",
                    severity="ERROR",
                    module="Customer",
                    affected_record_type="Customer",
                    affected_record_id=customer.id,
                    description="Customer contains missing mandatory data.",
                    details={
                        "customer_id": customer.id,
                        "missing_fields": missing_fields,
                    },
                )
            )

        if customer.deleted_at is not None and customer.status == "Active":
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="DELETED_ACTIVE_CUSTOMER",
                    severity="WARNING",
                    module="Customer",
                    affected_record_type="Customer",
                    affected_record_id=customer.id,
                    description="Deleted customer is still marked as Active.",
                    details={
                        "customer_id": customer.customer_id,
                        "deleted_at": customer.deleted_at.isoformat(),
                        "status": customer.status,
                    },
                )
            )

        db.flush()

        return issues


    @staticmethod
    def run_sale_lightweight_check(
        db: Session,
        company_id: int,
        sale_id: int,
    ):
        sale = (
            db.query(Sale)
            .filter(
                Sale.id == sale_id,
                Sale.company_id == company_id,
            )
            .first()
        )

        if not sale:
            return []

        issues = []

        if not sale.invoice_number:
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="MISSING_SALE_DATA",
                    severity="ERROR",
                    module="Sales",
                    affected_record_type="Sale",
                    affected_record_id=sale.id,
                    description="Sale invoice number is missing.",
                    details={
                        "sale_id": sale.id,
                        "invoice_number": sale.invoice_number,
                    },
                )
            )

        if not sale.customer_id:
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="INVALID_SALE_CUSTOMER",
                    severity="ERROR",
                    module="Sales",
                    affected_record_type="Sale",
                    affected_record_id=sale.id,
                    description="Sale does not have a valid customer.",
                    details={
                        "sale_id": sale.id,
                        "customer_id": sale.customer_id,
                    },
                )
            )

        if not sale.items:
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="SALE_WITHOUT_ITEMS",
                    severity="ERROR",
                    module="Sales",
                    affected_record_type="Sale",
                    affected_record_id=sale.id,
                    description="Sale does not contain any sale items.",
                    details={
                        "sale_id": sale.id,
                        "invoice_number": sale.invoice_number,
                    },
                )
            )

        calculated_total = 0

        for item in sale.items:
            if item.quantity <= 0:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_SALE_QUANTITY",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="SaleItem",
                        affected_record_id=item.id,
                        description="Sale item quantity must be greater than zero.",
                        details={
                            "sale_id": sale.id,
                            "sale_item_id": item.id,
                            "product_id": item.product_id,
                            "quantity": item.quantity,
                        },
                    )
                )

            if item.unit_price <= 0:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_SALE_ITEM_AMOUNT",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="SaleItem",
                        affected_record_id=item.id,
                        description="Sale item unit price must be greater than zero.",
                        details={
                            "sale_id": sale.id,
                            "sale_item_id": item.id,
                            "unit_price": item.unit_price,
                        },
                    )
                )

            expected_item_total = (
                (item.quantity * item.unit_price)
                - (item.discount or 0)
                + (item.tax or 0)
            )

            if abs(float(item.total) - float(expected_item_total)) > 0.01:
                issues.append(
                    DataQualityService.create_or_update_issue(
                        db=db,
                        company_id=company_id,
                        issue_type="INVALID_SALE_ITEM_AMOUNT",
                        severity="ERROR",
                        module="Sales",
                        affected_record_type="SaleItem",
                        affected_record_id=item.id,
                        description="Sale item total does not match its calculated amount.",
                        details={
                            "sale_id": sale.id,
                            "sale_item_id": item.id,
                            "quantity": item.quantity,
                            "unit_price": float(item.unit_price),
                            "discount": float(item.discount or 0),
                            "tax": float(item.tax or 0),
                            "expected_total": float(expected_item_total),
                            "actual_total": float(item.total),
                        },
                    )
                )

            calculated_total += float(item.total)

        expected_sale_total = (
            calculated_total
            - float(sale.discount or 0)
            + float(sale.tax or 0)
        )

        if abs(float(sale.total_amount) - expected_sale_total) > 0.01:
            issues.append(
                DataQualityService.create_or_update_issue(
                    db=db,
                    company_id=company_id,
                    issue_type="SALE_TOTAL_MISMATCH",
                    severity="ERROR",
                    module="Sales",
                    affected_record_type="Sale",
                    affected_record_id=sale.id,
                    description="Sale total does not match the calculated item totals.",
                    details={
                        "sale_id": sale.id,
                        "invoice_number": sale.invoice_number,
                        "expected_total": float(expected_sale_total),
                        "actual_total": float(sale.total_amount),
                        "difference": float(
                            sale.total_amount - expected_sale_total
                        ),
                    },
                )
            )

        db.flush()

        return issues