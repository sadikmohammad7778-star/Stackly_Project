from datetime import datetime, timedelta

from app.models.refresh_token import RefreshToken

from app.security.hashing import (
    hash_password,
    verify_password,
)

from app.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
)

from app.security.hashing import verify_password
from app.security.jwt_handler import create_access_token
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.company import Company
from app.schemas.user_schema import UserCreate
from app.security.hashing import hash_password
from app.services.audit_service import create_audit_log



def register_user(db: Session, user: UserCreate):

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    # Check if company exists
    company = (
        db.query(Company)
        .filter(Company.id == user.company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Create user
    new_user = User(
        company_id=user.company_id,
        name=user.name,
        email=user.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

from datetime import datetime, timedelta

from app.models.refresh_token import RefreshToken
from app.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
)


def login_user(db: Session, email: str, password: str):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Create Access Token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id
        }
    )

    # Create Refresh Token
    refresh_token = create_refresh_token()

   # Save Refresh Token in Database
    refresh = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    create_audit_log(
        db=db,
        user_id=user.id,
        action="LOGIN",
        module="Authentication"
    )

    try:
        db.add(refresh)
        db.commit()
        db.refresh(refresh)

        print("✅ Refresh Token Saved Successfully")
        print("Refresh ID:", refresh.id)
        print("Refresh Token:", refresh.token)

    except Exception as e:
        db.rollback()
        print("❌ Error while saving refresh token")
        print(e)
        raise

    print("Refresh Token ID:", refresh.id)

    count = db.query(RefreshToken).count()
    print("Refresh Token Count After Insert:", count)

    # Return both tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def refresh_access_token(db: Session, refresh_token: str):

    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token."
        )

    if token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired."
        )

    user = (
        db.query(User)
        .filter(User.id == token.user_id)
        .first()
    )

    access_token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }    


def logout_user(db: Session, refresh_token: str):
    print("Received Token:", repr(refresh_token))

    tokens = db.query(RefreshToken).all()

    print("Total Tokens:", len(tokens))

    for token_obj in tokens:
        print("-------------------------")
        print("DB Token :", repr(token_obj.token))
        print("API Token:", repr(refresh_token))
        print("Equal    :", token_obj.token == refresh_token)

    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    print("Query Result:", token)

    if not token:
        raise HTTPException(
            status_code=404,
            detail="Refresh token not found."
        )

    db.delete(token)
    db.commit()

    return {
        "message": "Logout successful."
    }