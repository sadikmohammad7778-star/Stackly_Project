from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company_schema import CompanyCreate, CompanyUpdate
from app.services.audit_service import create_audit_log


def create_company(
    db: Session,
    company: CompanyCreate,
    user_id: int,
    audit_company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
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

    try:
        db.add(new_company)
        db.flush()

        create_audit_log(
            db=db,
            company_id=audit_company_id,
            user_id=user_id,
            module="Company",
            action="CREATE",
            resource_type="Company",
            resource_id=str(new_company.id),
            description=f"Created company '{new_company.company_name}'",
            before_values=None,
            after_values={
                "company_name": new_company.company_name,
                "email": new_company.email,
                "phone": new_company.phone,
                "address": new_company.address,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(new_company)

        return new_company

    except Exception:
        db.rollback()
        raise


def get_all_companies(db: Session):
    return db.query(Company).all()


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


def update_company(
    db: Session,
    company_id: int,
    company: CompanyUpdate,
    user_id: int,
    audit_company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
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
            Company.id != company_id,
        )
        .first()
    )

    if duplicate_email:
        raise HTTPException(
            status_code=400,
            detail="Company email already exists."
        )

    before_values = {
        "company_name": existing_company.company_name,
        "email": existing_company.email,
        "phone": existing_company.phone,
        "address": existing_company.address,
    }

    existing_company.company_name = company.company_name
    existing_company.email = company.email
    existing_company.phone = company.phone
    existing_company.address = company.address

    after_values = {
        "company_name": existing_company.company_name,
        "email": existing_company.email,
        "phone": existing_company.phone,
        "address": existing_company.address,
    }

    try:
        create_audit_log(
            db=db,
            company_id=audit_company_id,
            user_id=user_id,
            module="Company",
            action="UPDATE",
            resource_type="Company",
            resource_id=str(existing_company.id),
            description=f"Updated company '{existing_company.company_name}'",
            before_values=before_values,
            after_values=after_values,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(existing_company)

        return existing_company

    except Exception:
        db.rollback()
        raise


def delete_company(
    db: Session,
    company_id: int,
    user_id: int,
    audit_company_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
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

    before_values = {
        "company_name": company.company_name,
        "email": company.email,
        "phone": company.phone,
        "address": company.address,
    }

    company_name = company.company_name
    company_id_value = company.id

    if audit_company_id == company_id_value:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete the company associated with your current account."
        )

    try:
        create_audit_log(
            db=db,
            company_id=audit_company_id,
            user_id=user_id,
            module="Company",
            action="DELETE",
            resource_type="Company",
            resource_id=str(company_id_value),
            description=f"Deleted company '{company_name}'",
            before_values=before_values,
            after_values=None,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.delete(company)
        db.commit()

        return {
            "message": "Company deleted successfully."
        }

    except Exception:
        db.rollback()
        raise