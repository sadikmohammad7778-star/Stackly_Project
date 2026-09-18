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
    create_report_history
)

from app.services.email_service import send_report_email

from app.schemas.report_schema import ReportFilters

from app.services.export_service import (
    generate_csv,
    generate_pdf
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
        return get_sales_report_data(
            db,
            report.company_id,
            filters
        )

    if report_type == "inventory":
        return get_inventory_report_data(
            db,
            report.company_id,
            filters
        )

    if report_type == "customers":
        return get_customer_report_data(
            db,
            report.company_id,
            filters
        )

    if report_type == "products":
        return get_product_performance_report_data(
            db,
            report.company_id,
            filters
        )

    if report_type == "stock-movements":
        return get_stock_movement_report_data(
            db,
            report.company_id,
            filters
        )

    raise ValueError(
        f"Unsupported report type: {report.report_type}"
    )


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
        "stock-movements": "Stock Movement Report"
    }

    return titles.get(
        report_type.lower(),
        "Report"
    )


def should_execute(report, now):
    frequency = report.frequency.lower()

    if not report.last_generated_at:
        return True

    last_generated = report.last_generated_at

    if frequency == "daily":
        return last_generated.date() < now.date()

    if frequency == "weekly":
        return (now - last_generated).total_seconds() >= 7 * 24 * 60 * 60

    if frequency == "monthly":
        return (
            last_generated.year != now.year
            or last_generated.month != now.month
        )

    return False

def create_report_file_path(report):
    os.makedirs(
        REPORT_DIRECTORY,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_type = (
        report.report_type
        .lower()
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

    return os.path.join(
        REPORT_DIRECTORY,
        file_name
    )


async def scheduled_report_worker():
    print("Scheduled report worker started")

    while True:
        db = SessionLocal()

        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")

            reports = (
                db.query(ScheduledReport)
                .filter(
                    ScheduledReport.is_active == True,
                    ScheduledReport.execution_time == current_time
                )
                .all()
            )

            for report in reports:
                if not should_execute(report, now):
                    continue

                await execute_scheduled_report(
                    db,
                    report
                )

        except Exception as error:
            print(
                f"Scheduled report worker error: {error}"
            )

        finally:
            db.close()

        await asyncio.sleep(30)


async def execute_scheduled_report(db, report):
    filters = parse_filters(report.filters)
    title = get_report_title(report.report_type)
    file_path = None

    try:
        print(
            f"Executing scheduled report: "
            f"{report.report_type} | "
            f"Company: {report.company_id} | "
            f"Format: {report.format}"
        )

        report_response = get_report_data(
            db,
            report,
            filters
        )

        data = get_report_items(report_response)

        filter_context = filters.model_dump(
            exclude_none=True,
            mode="json"
        )

        file_path = create_report_file_path(report)

        if report.format.upper() == "CSV":
            generate_csv(
                data,
                file_path
            )

        elif report.format.upper() == "PDF":
            generate_pdf(
                title,
                data,
                filter_context,
                file_path
            )

        else:
            raise ValueError(
                f"Unsupported format: {report.format}"
            )

        send_report_email(
            recipients=report.recipients,
            report_name=title,
            file_path=file_path
        )

        history = create_report_history(
            db=db,
            company_id=report.company_id,
            user_id=report.created_by,
            report_name=title,
            filters=filters,
            report_format=report.format,
            status="Success",
            error_message=None,
            file_path=file_path
        )

        report.last_generated_at = datetime.now()
        report.last_status = "Success"
        report.last_error = None

        db.commit()

        print(
            f"Report history created successfully: "
            f"ID {history.id}"
        )

        print(
            f"Scheduled report completed successfully: "
            f"ID {report.id}"
        )

    except Exception as error:
        db.rollback()

        error_message = str(error)

        print(
            f"Scheduled report failed: "
            f"ID {report.id} | "
            f"Error: {error_message}"
        )

        try:
            failed_history = create_report_history(
                db=db,
                company_id=report.company_id,
                user_id=report.created_by,
                report_name=title,
                filters=filters,
                report_format=report.format,
                status="Failed",
                error_message=error_message,
                file_path=file_path
            )

            report.last_generated_at = datetime.now()
            report.last_status = "Failed"
            report.last_error = error_message

            db.commit()

            print(
                f"Failed report history created: "
                f"ID {failed_history.id}"
            )

        except Exception as history_error:
            db.rollback()

            print(
                f"Failed to create failure history: "
                f"{history_error}"
            )

            try:
                report.last_generated_at = datetime.now()
                report.last_status = "Failed"
                report.last_error = error_message

                db.commit()

            except Exception as update_error:
                db.rollback()

                print(
                    f"Failed to update scheduled report: "
                    f"{update_error}"
                )