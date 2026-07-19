from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db

from app.schemas.report_schema import (
    SalesReport,
    StockReport,
)

from app.services.report_service import (
    get_sales_report,
    get_stock_report,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/sales",
    response_model=SalesReport,
)
def sales_report(
    db: Session = Depends(get_db),
):
    return get_sales_report(db)


@router.get(
    "/stock",
    response_model=StockReport,
)
def stock_report(
    db: Session = Depends(get_db),
):
    return get_stock_report(db)