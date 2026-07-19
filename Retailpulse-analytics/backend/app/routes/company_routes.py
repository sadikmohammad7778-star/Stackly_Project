from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.security.role_dependency import require_company_admin
from app.models.user import User
from app.services.company_service import (
    create_company,
    get_all_companies,
    get_company_by_id,
    update_company,
    delete_company
)
from app.schemas.company_schema import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)
router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=CompanyResponse)
def create_company_api(company: CompanyCreate, db: Session = Depends(get_db)):
    return create_company(db, company)


@router.get("/", response_model=list[CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    return get_all_companies(db)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    return get_company_by_id(db, company_id)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company_api(
    company_id: int,
    company: CompanyUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_company_admin),
):
    return update_company(db, company_id, company)

@router.delete("/{company_id}")
def delete_company_api(
    company_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_company_admin),
):
    return delete_company(db, company_id)