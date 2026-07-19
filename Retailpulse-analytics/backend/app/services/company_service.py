from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company_schema import CompanyCreate,CompanyUpdate
from app.services.audit_service import create_audit_log

def create_company(db: Session, company: CompanyCreate):
    existing_company = (
        db.query(Company)
        .filter(Company.email == company.email)
        .first()
    )

    if existing_company:
        raise HTTPException(
            status_code=400,
            detail="Company email already exists."
        )

    new_company = Company(
        company_name=company.company_name,
        email=company.email,
        phone=company.phone,
        address=company.address,
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    create_audit_log(
    db=db,
    user_id=1,      # Temporary for now
    action="CREATE",
    module="Company"
    )
    
    return new_company

    


def get_all_companies(db: Session):
    companies = db.query(Company).all()
    return companies

def get_company_by_id(db: Session, company_id: int):
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    return company

def update_company(db: Session, company_id: int, company: CompanyUpdate):
    existing_company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not existing_company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    duplicate_email = (
        db.query(Company)
        .filter(
            Company.email == company.email,
            Company.id != company_id
        )
        .first()
    )

    if duplicate_email:
        raise HTTPException(
            status_code=400,
            detail="Company email already exists."
        )

    existing_company.company_name = company.company_name
    existing_company.email = company.email
    existing_company.phone = company.phone
    existing_company.address = company.address

    db.commit()
    db.refresh(existing_company)

    return existing_company


def delete_company(db: Session, company_id: int):
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    db.delete(company)
    db.commit()

    return {
        "message": "Company deleted successfully."
    }