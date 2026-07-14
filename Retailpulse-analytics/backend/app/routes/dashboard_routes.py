from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.security.auth_dependency import get_current_user
from app.models.user import User
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboard_summary(db)