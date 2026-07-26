from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.dependency import get_db

from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserLogin,
    RefreshTokenRequest,
)

from app.services.user_service import (
    register_user,
    login_user,
    refresh_access_token,
    logout_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register User",
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    return register_user(db, user)


@router.post(
    "/login",
    summary="Login User",
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    return login_user(
        db,
        user.email,
        user.password,
    )


@router.post(
    "/refresh",
    summary="Refresh Access Token",
)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return refresh_access_token(
        db,
        request.refresh_token,
    )


@router.post(
    "/logout",
    summary="Logout User",
)
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return logout_user(
        db,
        request.refresh_token,
    )