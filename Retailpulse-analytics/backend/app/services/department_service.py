from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.company import Company
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate
from app.services.audit_service import create_audit_log


def create_department(
    db: Session,
    department: DepartmentCreate,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    existing = (
        db.query(Department)
        .filter(
            Department.department_name == department.department_name,
            Department.company_id == company_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Department already exists."
        )

    department_data = department.model_dump()
    department_data["company_id"] = company_id

    new_department = Department(**department_data)

    try:
        db.add(new_department)
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Department",
            action="CREATE",
            resource_type="Department",
            resource_id=str(new_department.id),
            description=(
                f"Created department "
                f"'{new_department.department_name}'"
            ),
            before_values=None,
            after_values={
                "department_name": new_department.department_name,
                "description": new_department.description,
                "company_id": new_department.company_id,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(new_department)

        return new_department

    except Exception:
        db.rollback()
        raise


def get_all_departments(
    db: Session,
    company_id: int = None,
):
    query = db.query(Department)

    if company_id is not None:
        query = query.filter(
            Department.company_id == company_id
        )

    return query.all()


def get_department_by_id(
    db: Session,
    department_id: int,
    company_id: int,
):
    department = (
        db.query(Department)
        .filter(
            Department.id == department_id,
            Department.company_id == company_id,
        )
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found."
        )

    return department


def update_department(
    db: Session,
    department_id: int,
    department: DepartmentUpdate,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    existing = (
        db.query(Department)
        .filter(
            Department.id == department_id,
            Department.company_id == company_id,
        )
        .first()
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Department not found."
        )

    department_data = department.model_dump(
        exclude_unset=True
    )

    if "department_name" in department_data:
        duplicate = (
            db.query(Department)
            .filter(
                Department.department_name == department_data["department_name"],
                Department.company_id == company_id,
                Department.id != department_id,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Department already exists."
            )

    before_values = {
        "department_name": existing.department_name,
        "description": existing.description,
        "company_id": existing.company_id,
    }

    for key, value in department_data.items():
        if key != "company_id":
            setattr(existing, key, value)

    existing.company_id = company_id

    after_values = {
        "department_name": existing.department_name,
        "description": existing.description,
        "company_id": existing.company_id,
    }

    try:
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Department",
            action="UPDATE",
            resource_type="Department",
            resource_id=str(existing.id),
            description=(
                f"Updated department "
                f"'{existing.department_name}'"
            ),
            before_values=before_values,
            after_values=after_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(existing)

        return existing

    except Exception:
        db.rollback()
        raise


def delete_department(
    db: Session,
    department_id: int,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    department = (
        db.query(Department)
        .filter(
            Department.id == department_id,
            Department.company_id == company_id,
        )
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found."
        )

    before_values = {
        "department_name": department.department_name,
        "description": department.description,
        "company_id": department.company_id,
    }

    department_name = department.department_name
    department_id_value = department.id

    try:
        db.delete(department)
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Department",
            action="DELETE",
            resource_type="Department",
            resource_id=str(department_id_value),
            description=f"Deleted department '{department_name}'",
            before_values=before_values,
            after_values=None,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()

        return {
            "message": "Department deleted successfully."
        }

    except Exception:
        db.rollback()
        raise