from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User

from app.services.company_service import (
    create_company,
    get_all_companies,
    get_company_by_id,
    update_company,
    delete_company,
)

from app.schemas.company_schema import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.post("/", response_model=CompanyResponse)
def create_company_api(
    company: CompanyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_company(
        db=db,
        company=company,
        user_id=current_user.id,
        audit_company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )


@router.get("/", response_model=list[CompanyResponse])
def get_companies(
    db: Session = Depends(get_db),
):
    return get_all_companies(db)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    return get_company_by_id(
        db,
        company_id,
    )


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company_api(
    company_id: int,
    company: CompanyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_company(
        db=db,
        company_id=company_id,
        company=company,
        user_id=current_user.id,
        audit_company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )


@router.delete("/{company_id}")
def delete_company_api(
    company_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_company(
        db=db,
        company_id=company_id,
        user_id=current_user.id,
        audit_company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )