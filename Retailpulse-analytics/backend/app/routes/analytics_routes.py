from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.security.auth_dependency import get_current_user

from app.services.analytics_service import (
    get_overview,
    employees_by_department,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_overview(db)


@router.get("/employees-by-department")
def employee_department(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return employees_by_department(db)