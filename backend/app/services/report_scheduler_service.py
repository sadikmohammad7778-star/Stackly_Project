import asyncio
import json
import os
from datetime import datetime

from app.config.database import SessionLocal
from app.models.scheduled_report import ScheduledReport

from app.services.report_service import (
    get_sales_report_data,
    get_inventory_report_data,
    get_customer_report_data,
    get_product_performance_report_data,
    get_stock_movement_report_data,
    create_report_history,
)

from app.services.system_health_service import (
    mark_worker_started,
    mark_worker_heartbeat,
    mark_worker_error,
    mark_worker_stopped,
    mark_worker_failed,
)

from app.services.email_service import send_report_email
from app.schemas.report_schema import ReportFilters

from app.services.export_service import (
    generate_csv,
    generate_pdf,
)


REPORT_DIRECTORY = "generated_reports"


def parse_filters(filters):
    if not filters:
        return ReportFilters()

    try:
        data = json.loads(filters)
        return ReportFilters(**data)
    except Exception:
        return ReportFilters()


def get_report_data(db, report, filters):
    report_type = report.report_type.lower()

    if report_type == "sales":
        return get_sales_report_data(db, report.company_id, filters)

    if report_type == "inventory":
        return get_inventory_report_data(db, report.company_id, filters)

    if report_type == "customers":
        return get_customer_report_data(db, report.company_id, filters)

    if report_type == "products":
        return get_product_performance_report_data(
            db,
            report.company_id,
            filters,
        )

    if report_type == "stock-movements":
        return get_stock_movement_report_data(
            db,
            report.company_id,
            filters,
        )

    raise ValueError(f"Unsupported report type: {report.report_type}")


def get_report_items(report_response):
    return [
        item.model_dump(mode="json")
        for item in report_response.data
    ]


def get_report_title(report_type):
    titles = {
        "sales": "Sales Report",
        "inventory": "Inventory Report",
        "customers": "Customer Report",
        "products": "Product Performance Report",
        "stock-movements": "Stock Movement Report",
    }

    return titles.get(report_type.lower(), "Report")


def should_execute(report, now):
    frequency = report.frequency.lower()

    if not report.last_generated_at:
        return True

    last_generated = report.last_generated_at

    if frequency == "daily":
        return last_generated.date() < now.date()

    if frequency == "weekly":
        return (
            now - last_generated
        ).total_seconds() >= 7 * 24 * 60 * 60

    if frequency == "monthly":
        return (
            last_generated.year != now.year
            or last_generated.month != now.month
        )

    return False


def create_report_file_path(report):
    os.makedirs(REPORT_DIRECTORY, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_type = (
        report.report_type.lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

    extension = report.format.lower()

    file_name = (
        f"{report_type}_"
        f"company_{report.company_id}_"
        f"{timestamp}."
        f"{extension}"
    )

    return os.path.join(REPORT_DIRECTORY, file_name)


async def execute_scheduled_report(db, report):
    filters = parse_filters(report.filters)
    report_name = get_report_title(report.report_type)
    file_path = create_report_file_path(report)

    try:
        report_response = get_report_data(
            db,
            report,
            filters,
        )

        report_items = get_report_items(report_response)

        if report.format.lower() == "csv":
            generate_csv(report_items, file_path)

        elif report.format.lower() == "pdf":
            generate_pdf(
                report_name,
                report_items,
                filters.model_dump(mode="json"),
                file_path,
            )

        else:
            raise ValueError(
                f"Unsupported report format: {report.format}"
            )

        if report.recipients:
            await asyncio.to_thread(
                send_report_email,
                report.recipients,
                report_name,
                file_path,
            )

        create_report_history(
            db=db,
            company_id=report.company_id,
            user_id=report.created_by,
            report_name=report_name,
            filters=filters,
            report_format=report.format,
            status="Success",
            file_path=file_path,
        )

        report.last_generated_at = datetime.now()
        report.last_status = "Success"
        report.last_error = None

        db.commit()

    except asyncio.CancelledError:
        raise

    except Exception as error:
        db.rollback()

        report.last_status = "Failed"
        report.last_error = str(error)

        create_report_history(
            db=db,
            company_id=report.company_id,
            user_id=report.created_by,
            report_name=report_name,
            filters=filters,
            report_format=report.format,
            status="Failed",
            error_message=str(error),
            file_path=(
                file_path
                if os.path.isfile(file_path)
                else None
            ),
        )

        db.commit()
        raise


async def scheduled_report_worker():
    print("Scheduled report worker started")

    mark_worker_started()

    try:
        while True:
            db = SessionLocal()
            cycle_failed = False

            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")

                reports = (
                    db.query(ScheduledReport)
                    .filter(
                        ScheduledReport.is_active.is_(True),
                        ScheduledReport.execution_time == current_time,
                    )
                    .all()
                )

                for report in reports:
                    if not should_execute(report, now):
                        continue

                    try:
                        await execute_scheduled_report(db, report)

                    except asyncio.CancelledError:
                        raise

                    except Exception:
                        cycle_failed = True
                        continue

                if cycle_failed:
                    mark_worker_error(
                        "One or more scheduled reports failed"
                    )
                else:
                    mark_worker_heartbeat()

            except asyncio.CancelledError:
                raise

            except Exception:
                mark_worker_error(
                    "Scheduled report polling cycle failed"
                )

            finally:
                try:
                    db.close()
                except Exception:
                    mark_worker_error(
                        "Failed to close scheduled report database session"
                    )

            await asyncio.sleep(30)

    except asyncio.CancelledError:
        mark_worker_stopped()
        raise

    except Exception:
        mark_worker_failed(
            "Scheduled report worker terminated unexpectedly"
        )
        raise