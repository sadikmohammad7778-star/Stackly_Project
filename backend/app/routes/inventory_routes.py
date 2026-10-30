from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.models.user import User
from app.services.inventory_service import InventoryService
from app.schemas.inventory_schema import (
    AddStockRequest,
    RemoveStockRequest,
    AdjustStockRequest,
)
from app.security.permission_dependency import require_permission


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.get("/")
def get_inventory(
    search: str = None,
    category: int = None,
    brand: str = None,
    status: str = None,
    sort: str = None,
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory", "view")
    ),
):
    return InventoryService.get_inventory(
        db,
        current_user.company_id,
        search,
        category,
        brand,
        status,
        sort,
        order,
    )

@router.post("/add-stock")
def add_stock(
    data: AddStockRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory", "update")
    ),
):
    return InventoryService.add_stock(
        db,
        data,
        current_user.id,
        current_user.company_id,
        ip_address=(
            request.client.host if request.client else None
        ),
        user_agent=request.headers.get("user-agent"),
    )

@router.post("/remove-stock")
def remove_stock(
    data: RemoveStockRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory", "update")
    ),
):
    return InventoryService.remove_stock(
        db,
        data,
        current_user.id,
        current_user.company_id,
        ip_address=(
            request.client.host if request.client else None
        ),
        user_agent=request.headers.get("user-agent"),
    )

@router.post("/adjust-stock")
def adjust_stock(
    data: AdjustStockRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory", "update")
    ),
):
    return InventoryService.adjust_stock(
        db,
        data,
        current_user.id,
        current_user.company_id,
        ip_address=(
            request.client.host if request.client else None
        ),
        user_agent=request.headers.get("user-agent"),
    )

@router.get("/movements")
def get_movement_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory", "view")
    ),
):
    return InventoryService.get_movement_history(
        db,
        current_user.company_id,
    )


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory", "view")
    ),
):
    return InventoryService.get_dashboard(
        db,
        current_user.company_id,
    )

@router.get("/category-chart")
def category_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory", "view")
    ),
):
    return InventoryService.inventory_by_category(
        db,
        current_user.company_id,
    )

@router.get("/status-chart")
def status_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("inventory", "view")
    ),
):
    return InventoryService.stock_status_distribution(
        db,
        current_user.company_id,
    )