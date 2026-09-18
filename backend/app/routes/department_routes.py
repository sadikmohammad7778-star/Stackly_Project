from fastapi import APIRouter, Depends, Request
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


@router.post("/", response_model=DepartmentResponse)
def create_department_api(
    department: DepartmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_department(
        db=db,
        department=department,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.get("/", response_model=list[DepartmentResponse])
def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_departments(
        db=db,
        company_id=current_user.company_id,
    )


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_department_by_id(
        db=db,
        department_id=department_id,
        company_id=current_user.company_id,
    )


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department_api(
    department_id: int,
    department: DepartmentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_department(
        db=db,
        department_id=department_id,
        department=department,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.delete("/{department_id}")
def delete_department_api(
    department_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_department(
        db=db,
        department_id=department_id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )