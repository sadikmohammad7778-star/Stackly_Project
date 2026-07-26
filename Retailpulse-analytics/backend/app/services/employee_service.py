from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.company import Company
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from app.services.audit_service import create_audit_log


# ---------------------------------
# Create Employee
# ---------------------------------
def create_employee(
    db: Session,
    employee: EmployeeCreate,
    user_id: int,
):

    company = (
        db.query(Company)
        .filter(Company.id == employee.company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    existing = (
        db.query(Employee)
        .filter(Employee.email == employee.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Employee email already exists."
        )

    new_employee = Employee(**employee.model_dump())

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    create_audit_log(
        db=db,
        company_id=new_employee.company_id,
        user_id=user_id,
        module="Employee",
        action="CREATE",
        description=(
            f"Created employee "
            f"'{new_employee.first_name} {new_employee.last_name}'"
        ),
    )

    return new_employee


# ---------------------------------
# Get All Employees
# ---------------------------------
def get_all_employees(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: str = "",
):

    query = db.query(Employee)

    if search:
        query = query.filter(
            or_(
                Employee.first_name.ilike(f"%{search}%"),
                Employee.last_name.ilike(f"%{search}%"),
                Employee.email.ilike(f"%{search}%"),
            )
        )

    return (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )


# ---------------------------------
# Get Employee By ID
# ---------------------------------
def get_employee_by_id(
    db: Session,
    employee_id: int,
):

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return employee


# ---------------------------------
# Update Employee
# ---------------------------------
def update_employee(
    db: Session,
    employee_id: int,
    employee: EmployeeUpdate,
    user_id: int,
):

    existing = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
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
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Employee email already exists."
            )

    for key, value in employee.model_dump(exclude_unset=True).items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    create_audit_log(
        db=db,
        company_id=existing.company_id,
        user_id=user_id,
        module="Employee",
        action="UPDATE",
        description=(
            f"Updated employee "
            f"'{existing.first_name} {existing.last_name}'"
        ),
    )

    return existing


# ---------------------------------
# Delete Employee
# ---------------------------------
def delete_employee(
    db: Session,
    employee_id: int,
    user_id: int,
):

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    employee_name = f"{employee.first_name} {employee.last_name}"
    company_id = employee.company_id

    db.delete(employee)
    db.commit()

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Employee",
        action="DELETE",
        description=f"Deleted employee '{employee_name}'",
    )

    return {
        "message": "Employee deleted successfully."
    }