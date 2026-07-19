from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.attendance import Attendance

from app.models.sale import Sale
from app.models.product import Product

from app.schemas.analytics_schema import (
    RevenueReport,
    InventoryReport,
)


def get_overview(db: Session):
    total_companies = db.query(Company).count()
    total_departments = db.query(Department).count()
    total_employees = db.query(Employee).count()

    active_employees = (
        db.query(Employee)
        .filter(Employee.status == True)
        .count()
    )

    inactive_employees = (
        db.query(Employee)
        .filter(Employee.status == False)
        .count()
    )

    total_attendance = db.query(Attendance).count()

    return {
        "total_companies": total_companies,
        "total_departments": total_departments,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
        "attendance_records": total_attendance,
    }


def employees_by_department(db: Session):
    return (
        db.query(
            Department.department_name,
            func.count(Employee.id).label("employees")
        )
        .join(
            Employee,
            Employee.department_id == Department.id
        )
        .group_by(Department.department_name)
        .all()
    )




def get_revenue_report(db: Session):
    now = datetime.utcnow()

    today = now.date()
    week_start = now - timedelta(days=7)
    month_start = now.replace(day=1)
    year_start = now.replace(month=1, day=1)

    today_revenue = (
        db.query(func.sum(Sale.total_amount))
        .filter(func.date(Sale.created_at) == today)
        .scalar() or 0
    )

    week_revenue = (
        db.query(func.sum(Sale.total_amount))
        .filter(Sale.created_at >= week_start)
        .scalar() or 0
    )

    month_revenue = (
        db.query(func.sum(Sale.total_amount))
        .filter(Sale.created_at >= month_start)
        .scalar() or 0
    )

    year_revenue = (
        db.query(func.sum(Sale.total_amount))
        .filter(Sale.created_at >= year_start)
        .scalar() or 0
    )

    return RevenueReport(
        today=today_revenue,
        this_week=week_revenue,
        this_month=month_revenue,
        this_year=year_revenue,
    )


def get_inventory_report(db: Session):

    total_products = db.query(Product).count()

    in_stock = db.query(Product).filter(Product.stock_quantity > 10).count()

    low_stock = db.query(Product).filter(
        Product.stock_quantity.between(1, 10)
    ).count()

    out_of_stock = db.query(Product).filter(
        Product.stock_quantity == 0
    ).count()

    inventory_value = (
        db.query(
            func.sum(Product.stock_quantity * Product.price)
        ).scalar() or 0
    )

    return InventoryReport(
        total_products=total_products,
        in_stock=in_stock,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        inventory_value=inventory_value,
    )