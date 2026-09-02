from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.company import Company
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from app.services.audit_service import create_audit_log


def create_employee(
    db: Session,
    employee: EmployeeCreate,
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
        db.query(Employee)
        .filter(
            Employee.email == employee.email,
            Employee.company_id == company_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Employee email already exists."
        )

    employee_data = employee.model_dump()
    employee_data["company_id"] = company_id

    new_employee = Employee(
        **employee_data,
        employee_code="TEMP",
    )

    try:
        db.add(new_employee)
        db.flush()

        new_employee.employee_code = f"EMP{new_employee.id:03d}"
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Employee",
            action="CREATE",
            resource_type="Employee",
            resource_id=str(new_employee.id),
            description=(
                f"Created employee "
                f"'{new_employee.first_name} {new_employee.last_name}'"
            ),
            before_values=None,
            after_values={
                "employee_code": new_employee.employee_code,
                "first_name": new_employee.first_name,
                "last_name": new_employee.last_name,
                "email": new_employee.email,
                "phone": new_employee.phone,
                "designation": new_employee.designation,
                "salary": new_employee.salary,
                "joining_date": (
                    new_employee.joining_date.isoformat()
                    if new_employee.joining_date
                    else None
                ),
                "status": new_employee.status,
                "department_id": new_employee.department_id,
                "company_id": new_employee.company_id,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(new_employee)

        return new_employee

    except Exception:
        db.rollback()
        raise

def get_all_employees(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: str = "",
    company_id: int = None,
):
    query = (
        db.query(Employee)
        .filter(Employee.company_id == company_id)
    )

    if search:
        query = query.filter(
            or_(
                Employee.first_name.ilike(f"%{search}%"),
                Employee.last_name.ilike(f"%{search}%"),
                Employee.email.ilike(f"%{search}%"),
                Employee.employee_code.ilike(f"%{search}%"),
            )
        )

    return (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )


def get_employee_by_id(
    db: Session,
    employee_id: int,
    company_id: int,
):
    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return employee


def update_employee(
    db: Session,
    employee_id: int,
    employee: EmployeeUpdate,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    existing = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    if employee.email:
        duplicate = (
            db.query(Employee)
            .filter(
                Employee.email == employee.email,
                Employee.id != employee_id,
                Employee.company_id == company_id,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Employee email already exists."
            )

    before_values = {
        "employee_code": existing.employee_code,
        "first_name": existing.first_name,
        "last_name": existing.last_name,
        "email": existing.email,
        "phone": existing.phone,
        "designation": existing.designation,
        "salary": existing.salary,
        "joining_date": (
            existing.joining_date.isoformat()
            if existing.joining_date
            else None
        ),
        "status": existing.status,
        "department_id": existing.department_id,
        "company_id": existing.company_id,
    }

    update_data = employee.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        if key not in ["company_id", "employee_code"]:
            setattr(existing, key, value)

    existing.company_id = company_id

    after_values = {
        "employee_code": existing.employee_code,
        "first_name": existing.first_name,
        "last_name": existing.last_name,
        "email": existing.email,
        "phone": existing.phone,
        "designation": existing.designation,
        "salary": existing.salary,
        "joining_date": (
            existing.joining_date.isoformat()
            if existing.joining_date
            else None
        ),
        "status": existing.status,
        "department_id": existing.department_id,
        "company_id": existing.company_id,
    }

    try:
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Employee",
            action="UPDATE",
            resource_type="Employee",
            resource_id=str(existing.id),
            description=(
                f"Updated employee "
                f"'{existing.first_name} {existing.last_name}'"
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


def delete_employee(
    db: Session,
    employee_id: int,
    user_id: int,
    company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.company_id == company_id,
        )
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    employee_name = (
        f"{employee.first_name} {employee.last_name}"
    )

    before_values = {
        "employee_code": employee.employee_code,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "phone": employee.phone,
        "designation": employee.designation,
        "salary": employee.salary,
        "joining_date": (
            employee.joining_date.isoformat()
            if employee.joining_date
            else None
        ),
        "status": employee.status,
        "department_id": employee.department_id,
        "company_id": employee.company_id,
    }

    employee_id_value = employee.id

    try:
        db.delete(employee)
        db.flush()

        create_audit_log(
            db=db,
            company_id=company_id,
            user_id=user_id,
            module="Employee",
            action="DELETE",
            resource_type="Employee",
            resource_id=str(employee_id_value),
            description=f"Deleted employee '{employee_name}'",
            before_values=before_values,
            after_values=None,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()

        return {
            "message": "Employee deleted successfully."
        }

    except Exception:
        db.rollback()
        raise