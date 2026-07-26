from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User

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


# Create Department
@router.post("/", response_model=DepartmentResponse)
def create_department_api(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_department(
        db,
        department,
        current_user.id,
    )


# Get All Departments
@router.get("/", response_model=list[DepartmentResponse])
def get_departments(
    db: Session = Depends(get_db),
):
    return get_all_departments(db)


# Get Department By ID
@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
):
    return get_department_by_id(
        db,
        department_id,
    )


# Update Department
@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department_api(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_department(
        db,
        department_id,
        department,
        current_user.id,
    )


# Delete Department
@router.delete("/{department_id}")
def delete_department_api(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_department(
        db,
        department_id,
        current_user.id,
    )