from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import register_user
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserLogin,
)
from app.services.user_service import (
    register_user,
    login_user,
)

from app.services.user_service import logout_user

from app.schemas.user_schema import RefreshTokenRequest
from app.services.user_service import refresh_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return register_user(db, user)

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    return login_user(
        db,
        user.email,
        user.password
    )

@router.post("/refresh")
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return refresh_access_token(
        db,
        request.refresh_token
    )


@router.post("/logout")
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return logout_user(
        db,
        request.refresh_token
    )