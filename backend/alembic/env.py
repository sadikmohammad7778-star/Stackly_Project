from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config.config import DATABASE_URL
from app.config.database import Base

# Import models so SQLAlchemy registers their tables.
from app.models.company import Company
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import Attendance
from app.models.category import Category
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.notification import Notification
from app.models.demand_forecast import DemandForecast
from app.models.forecast_history import ForecastHistory
from app.models.data_import import DataImport
from app.models.import_error import ImportError
from app.models.report_history import ReportHistory
from app.models.scheduled_report import ScheduledReport
from app.models.data_quality import DataQualityIssue, ReconciliationRun
from app.models.approval_request import ApprovalRequest
from app.models.approval_history import ApprovalHistory
from app.models.workflow_config import WorkflowConfiguration
from app.models.background_job import BackgroundJob
from app.models.permission import Permission
from app.models.role_permission import RolePermission

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use the application's existing database URL.
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%"),
)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()