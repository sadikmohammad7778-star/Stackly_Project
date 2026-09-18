from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.config.dependency import (
    get_db,
    get_current_user,
)

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
    request: Request,
    db: Session = Depends(get_db),
):
    return register_user(
        db=db,
        user=user,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )


@router.post(
    "/login",
    summary="Login User",
)
def login(
    user: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    return login_user(
        db=db,
        email=user.email,
        password=user.password,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
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
    http_request: Request,
    db: Session = Depends(get_db),
):
    return logout_user(
        db=db,
        refresh_token=request.refresh_token,
        ip_address=(
            http_request.client.host
            if http_request.client
            else None
        ),
        user_agent=http_request.headers.get("user-agent"),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
)
def get_me(
    current_user=Depends(get_current_user),
):
    return current_user