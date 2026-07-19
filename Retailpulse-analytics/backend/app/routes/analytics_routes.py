from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db

from app.schemas.analytics_schema import (
    RevenueReport,
    InventoryReport,
)

from app.services.analytics_service import (
    get_revenue_report,
    get_inventory_report,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/revenue",
    response_model=RevenueReport,
)
def revenue_report(db: Session = Depends(get_db)):
    return get_revenue_report(db)


@router.get(
    "/inventory",
    response_model=InventoryReport,
)
def inventory_report(db: Session = Depends(get_db)):
    return get_inventory_report(db)