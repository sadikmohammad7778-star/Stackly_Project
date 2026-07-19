from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.company import Company
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from app.services.audit_service import create_audit_log


def create_employee(db: Session, employee: EmployeeCreate):

    company = db.query(Company).filter(
        Company.id == employee.company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    existing = db.query(Employee).filter(
        Employee.email == employee.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Employee email already exists."
        )

    new_employee = Employee(**employee.model_dump())

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

#     create_audit_log(
#     db=db,
#     user_id=1,
#     action="CREATE",
#     module="Employee"
#    )
    return new_employee

from sqlalchemy import or_

def get_all_employees(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: str = ""
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

    employees = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return employees


def get_employee_by_id(db: Session, employee_id: int):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return employee


def update_employee(
    db: Session,
    employee_id: int,
    employee: EmployeeUpdate
):
    existing = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    # Check duplicate email
    if employee.email:
        duplicate = (
            db.query(Employee)
            .filter(
                Employee.email == employee.email,
                Employee.id != employee_id
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

    return existing


def delete_employee(db: Session, employee_id: int):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    db.delete(employee)
    db.commit()

    return {
        "message": "Employee deleted successfully."
    }