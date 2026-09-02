from fastapi import APIRouter, Depends, Query, Request

from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User

from app.schemas.employee_schema import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)

from app.services.employee_service import (
    create_employee,
    get_all_employees,
    get_employee_by_id,
    update_employee,
    delete_employee,
)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post("/", response_model=EmployeeResponse)
def create(
    employee: EmployeeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_employee(
        db=db,
        employee=employee,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )


@router.get("/", response_model=list[EmployeeResponse])
def get_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_employees(
        db=db,
        company_id=current_user.company_id,
        page=page,
        limit=limit,
        search=search,
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_by_id(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_employee_by_id(
        db,
        employee_id,
        current_user.company_id,
    )


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update(
    employee_id: int,
    employee: EmployeeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_employee(
        db=db,
        employee_id=employee_id,
        employee=employee,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )


@router.delete("/{employee_id}")
def delete(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_employee(
        db=db,
        employee_id=employee_id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )