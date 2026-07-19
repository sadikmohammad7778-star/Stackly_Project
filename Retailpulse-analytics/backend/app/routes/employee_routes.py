from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session

from app.config.dependency import get_db

from app.models.user import User

from app.security.auth_dependency import get_current_user
from app.security.role_dependency import require_company_admin

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


# Create Employee (Company Admin Only)
@router.post("/", response_model=EmployeeResponse)
def create(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_company_admin),
):
    return create_employee(db, employee)



# Get Employee By ID (Any Logged-in User)

@router.get("/", response_model=list[EmployeeResponse])
def get_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = "",
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
):
    return get_all_employees(
        db=db,
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
    return get_employee_by_id(db, employee_id)


# Update Employee (Company Admin Only)
@router.put("/{employee_id}", response_model=EmployeeResponse)
def update(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_company_admin),
):
    return update_employee(db, employee_id, employee)


# Delete Employee (Company Admin Only)
@router.delete("/{employee_id}")
def delete(
    employee_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_company_admin),
):
    return delete_employee(db, employee_id)