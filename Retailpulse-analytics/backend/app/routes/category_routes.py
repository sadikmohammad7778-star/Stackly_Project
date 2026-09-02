from typing import List

from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.user import User

from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)

from app.services import category_service


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.create_category(
        db=db,
        category=category,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.get_all_categories(
        db,
        current_user.company_id,
    )


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.get_category_by_id(
        db,
        category_id,
        current_user.company_id,
    )


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.update_category(
        db=db,
        category_id=category_id,
        category=category,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.delete_category(
        db=db,
        category_id=category_id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
    )