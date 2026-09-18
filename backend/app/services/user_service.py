from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.security.hashing import hash_password, verify_password
from app.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
)
from app.services.audit_service import create_audit_log


def register_user(
    db: Session,
    user: UserCreate,
    ip_address: str = None,
    user_agent: str = None,
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered.",
        )

    company = (
        db.query(Company)
        .filter(Company.id == user.company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found.",
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        company_id=user.company_id,
        name=user.name,
        email=user.email,
        password=hashed_password,
    )

    try:
        db.add(new_user)
        db.flush()

        create_audit_log(
            db=db,
            company_id=new_user.company_id,
            user_id=new_user.id,
            module="Authentication",
            action="REGISTER",
            resource_type="User",
            resource_id=str(new_user.id),
            description=f"Registered user '{new_user.email}'",
            after_values={
                "name": new_user.name,
                "email": new_user.email,
                "company_id": new_user.company_id,
                "role": new_user.role,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to register user.",
        )


def login_user(
    db: Session,
    email: str,
    password: str,
    ip_address: str = None,
    user_agent: str = None,
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,
            "company_id": user.company_id,
            "role": user.role,
        }
    )

    refresh_token = create_refresh_token()

    refresh = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )

    try:
        db.add(refresh)
        db.flush()

        create_audit_log(
            db=db,
            company_id=user.company_id,
            user_id=user.id,
            module="Authentication",
            action="LOGIN",
            resource_type="User",
            resource_id=str(user.id),
            description=f"User '{user.email}' logged in",
            after_values={
                "email": user.email,
                "name": user.name,
                "company_id": user.company_id,
                "role": user.role,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.commit()
        db.refresh(refresh)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "company_id": user.company_id,
                "role": user.role,
            },
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Login failed.",
        )


def refresh_access_token(
    db: Session,
    refresh_token: str,
):
    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
        )

    if token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired.",
        )

    user = (
        db.query(User)
        .filter(User.id == token.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    access_token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,
            "company_id": user.company_id,
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


def logout_user(
    db: Session,
    refresh_token: str,
    ip_address: str = None,
    user_agent: str = None,
):
    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    if not token:
        raise HTTPException(
            status_code=404,
            detail="Refresh token not found.",
        )

    user = (
        db.query(User)
        .filter(User.id == token.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    try:
        create_audit_log(
            db=db,
            company_id=user.company_id,
            user_id=user.id,
            module="Authentication",
            action="LOGOUT",
            resource_type="User",
            resource_id=str(user.id),
            description=f"User '{user.email}' logged out",
            before_values={
                "email": user.email,
                "name": user.name,
                "company_id": user.company_id,
                "role": user.role,
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS",
        )

        db.delete(token)
        db.commit()

        return {
            "message": "Logout successful.",
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Logout failed.",
        )