from sqlalchemy.orm import Session

from app.config.database import SessionLocal

# Import models to register SQLAlchemy relationships.
import app.models.company
import app.models.user
import app.models.demand_forecast
import app.models.forecast_history
import app.models.import_history
import app.models.data_import
import app.models.import_error
import app.models.report_history
import app.models.scheduled_report
import app.models.data_quality
import app.models.approval_request
import app.models.approval_history
import app.models.workflow_config

from app.models.permission import Permission
from app.models.role_permission import RolePermission


PERMISSIONS = [
    ("dashboard", "view"),
    ("analytics", "view"),
    ("analytics", "export"),
    ("products", "view"),
    ("products", "create"),
    ("products", "update"),
    ("products", "delete"),
    ("inventory", "view"),
    ("inventory", "create"),
    ("inventory", "update"),
    ("inventory", "delete"),
    ("sales", "view"),
    ("sales", "create"),
    ("sales", "update"),
    ("sales", "delete"),
    ("customers", "view"),
    ("customers", "create"),
    ("customers", "update"),
    ("customers", "delete"),
    ("reports", "view"),
    ("reports", "export"),
    ("data_imports", "view"),
    ("data_imports", "create"),
    ("workflows", "view"),
    ("workflows", "approve"),
    ("audit_logs", "view"),
    ("system_monitoring", "view"),
    ("data_governance", "view"),
    ("data_governance", "manage_access"),
]


def seed_permissions(db: Session) -> None:
    """Create permissions that do not already exist."""

    created_count = 0

    try:
        for module, action in PERMISSIONS:
            code = f"{module}.{action}"

            permission = (
                db.query(Permission)
                .filter(Permission.code == code)
                .first()
            )

            if permission is None:
                permission = Permission(
                    module=module,
                    action=action,
                    code=code,
                    description=f"{action.title()} access for {module}",
                    is_active=True,
                )

                db.add(permission)
                created_count += 1

        db.commit()

        print("Permission catalog initialized successfully.")
        print(f"New permissions created: {created_count}")

    except Exception:
        db.rollback()
        raise


def assign_report_view_permission(db: Session) -> None:
    """Assign reports.view to the Analyst role for testing."""

    permission = (
        db.query(Permission)
        .filter(
            Permission.code == "reports.view",
            Permission.is_active.is_(True),
        )
        .first()
    )

    if permission is None:
        raise RuntimeError(
            "The active reports.view permission was not found."
        )

    role_name = "Analyst"

    existing_assignment = (
        db.query(RolePermission)
        .filter(
            RolePermission.role == role_name,
            RolePermission.permission_id == permission.id,
        )
        .first()
    )

    if existing_assignment:
        print(
            f"Permission reports.view is already assigned "
            f"to {role_name}."
        )
        return

    assignment = RolePermission(
        role=role_name,
        permission_id=permission.id,
    )

    try:
        db.add(assignment)
        db.commit()

        print(
            f"Successfully assigned reports.view to {role_name}."
        )

    except Exception:
        db.rollback()
        raise


def main() -> None:
    db = SessionLocal()

    try:
        seed_permissions(db)
        assign_report_view_permission(db)

        print("Permission initialization completed.")

    except Exception as exc:
        db.rollback()
        print(f"Permission initialization failed: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
    