from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.company import Company
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate


def create_department(
    db: Session,
    department: DepartmentCreate,
    user_id: int,
):
    company = db.query(Company).filter(
        Company.id == department.company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    existing = db.query(Department).filter(
        Department.department_name == department.department_name,
        Department.company_id == department.company_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Department already exists."
        )

    new_department = Department(**department.model_dump())

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        module="Department",
    )

    return new_department
def get_all_departments(db: Session):
    return db.query(Department).all()


def get_department_by_id(db: Session, department_id: int):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

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
):
    existing = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Department not found."
        )

    for key, value in department.model_dump(exclude_unset=True).items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        module="Department",
    )

    return existing

def delete_department(
    db: Session,
    department_id: int,
    user_id: int,
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found."
        )

    db.delete(department)
    db.commit()

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        module="Department",
    )

    return {
        "message": "Department deleted successfully."
    }