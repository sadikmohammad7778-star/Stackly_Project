from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db

from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)

from app.services.department_service import (
    create_department,
    get_all_departments,
    get_department_by_id,
    update_department,
    delete_department,
)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post("/", response_model=DepartmentResponse)
def create_department_api(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
):
    return create_department(db, department)


@router.get("/", response_model=list[DepartmentResponse])
def get_departments(
    db: Session = Depends(get_db),
):
    return get_all_departments(db)


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
):
    return get_department_by_id(db, department_id)


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department_api(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
):
    return update_department(db, department_id, department)


@router.delete("/{department_id}")
def delete_department_api(
    department_id: int,
    db: Session = Depends(get_db),
):
    return delete_department(db, department_id)