from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date


from app.models.sale_item import SaleItem
from app.models.category import Category
from app.models.inventory import Inventory


from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.sale import Sale
from app.models.product import Product


from app.schemas.analytics_schema import DashboardKPIs
from app.schemas.analytics_schema import (
    RevenueReport,
    InventoryReport,
)
from app.schemas.analytics_schema import SalesSummaryResponse

def apply_date_filter(
    query,
    date_from=None,
    date_to=None,
):
    if date_from:
        query = query.filter(
            Sale.sale_date >= date_from
        )

    if date_to:
        query = query.filter(
            Sale.sale_date < date_to
        )

    return query

def get_date_range(date_range: str):
    today = datetime.utcnow().date()

    if date_range == "today":
        return today, today + timedelta(days=1)

    if date_range == "last_7_days":
        return today - timedelta(days=6), today + timedelta(days=1)

    if date_range == "last_30_days":
        return today - timedelta(days=29), today + timedelta(days=1)

    if date_range == "this_month":
        start = today.replace(day=1)
        return start, today + timedelta(days=1)

    if date_range == "last_month":
        this_month = today.replace(day=1)
        last_month_end = this_month
        last_month_start = (
            this_month - timedelta(days=1)
        ).replace(day=1)

        return last_month_start, last_month_end

    if date_range == "all":
        return None, None

    raise ValueError(
        "Invalid date range"
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

    in_stock = (
        db.query(Product)
        .filter(Product.stock_quantity > 10)
        .count()
    )

    low_stock = (
        db.query(Product)
        .filter(Product.stock_quantity.between(1, 10))
        .count()
    )

    out_of_stock = (
        db.query(Product)
        .filter(Product.stock_quantity == 0)
        .count()
    )

    inventory_value = (
        db.query(
            func.sum(Product.stock_quantity * Product.unit_price)
        ).scalar() or 0
    )

    return InventoryReport(
        total_products=total_products,
        in_stock=in_stock,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        inventory_value=inventory_value,
    )



def get_dashboard_kpis(db: Session, company_id: int):
    """
    Dashboard KPI calculations
    """

    # Total Revenue
    total_revenue = (
        db.query(func.coalesce(func.sum(Sale.total_amount), 0))
        .filter(Sale.company_id == company_id)
        .scalar()
    )

    # Total Orders
    total_orders = (
        db.query(Sale)
        .filter(Sale.company_id == company_id)
        .count()
    )

    # Total Products Sold
    total_products_sold = (
        db.query(func.coalesce(func.sum(SaleItem.quantity), 0))
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.company_id == company_id)
        .scalar()
    )

    # Average Order Value
    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    # Inventory Value
    total_inventory_value = (
        db.query(
            func.coalesce(
                func.sum(
                    Inventory.available_stock * Product.unit_price
                ),
                0
            )
        )
        .join(Product, Product.id == Inventory.product_id)
        .filter(Inventory.company_id == company_id)
        .scalar()
    )

    # Low Stock Products
    low_stock_products = (
        db.query(Inventory)
        .filter(
            Inventory.company_id == company_id,
            Inventory.available_stock <= Inventory.reorder_level,
            Inventory.available_stock > 0,
        )
        .count()
    )

    # Out Of Stock Products
    out_of_stock_products = (
        db.query(Inventory)
        .filter(
            Inventory.company_id == company_id,
            Inventory.available_stock == 0,
        )
        .count()
    )

    # Total Categories
    total_categories = (
        db.query(Category)
        .filter(Category.company_id == company_id)
        .count()
    )

    return DashboardKPIs(
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_products_sold=total_products_sold,
        average_order_value=round(average_order_value, 2),
        total_inventory_value=total_inventory_value,
        low_stock_products=low_stock_products,
        out_of_stock_products=out_of_stock_products,
        total_categories=total_categories,
    )


def get_revenue_trend(
    db: Session,
    company_id: int,
    period: str = "daily",
    date_from=None,
    date_to=None,
):
    """
    Revenue trend by daily, weekly, or monthly period.
    """

    if period not in ["daily", "weekly", "monthly"]:
        raise ValueError(
            "Period must be daily, weekly, or monthly"
        )

    if period == "daily":
        date_group = cast(
            Sale.sale_date,
            Date
        )

    elif period == "weekly":
        date_group = func.date_trunc(
            "week",
            Sale.sale_date
        )

    else:
        date_group = func.date_trunc(
            "month",
            Sale.sale_date
        )

    query = (
        db.query(
            date_group.label("date"),
            func.coalesce(
                func.sum(Sale.total_amount),
                0
            ).label("revenue"),
        )
        .filter(
            Sale.company_id == company_id
        )
    )

    query = apply_date_filter(
        query,
        date_from,
        date_to,
    )

    data = (
        query
        .group_by(date_group)
        .order_by(date_group)
        .all()
    )

    return [
        {
            "date": str(row.date.date())
            if hasattr(row.date, "date")
            else str(row.date),
            "revenue": float(row.revenue),
        }
        for row in data
    ]
def get_top_products(
    db: Session,
    company_id: int,
    sort_by: str = "revenue",
    date_from=None,
    date_to=None,
):
    """
    Top performing products by revenue or quantity sold.
    """

    if sort_by not in ["revenue", "quantity"]:
        raise ValueError(
            "sort_by must be revenue or quantity"
        )

    revenue = func.coalesce(
        func.sum(SaleItem.total),
        0
    )

    quantity = func.coalesce(
        func.sum(SaleItem.quantity),
        0
    )

    if sort_by == "revenue":
        order_column = revenue.desc()
    else:
        order_column = quantity.desc()

    query = (
        db.query(
            Product.name.label("product_name"),
            quantity.label("quantity_sold"),
            revenue.label("revenue"),
        )
        .join(
            SaleItem,
            SaleItem.product_id == Product.id
        )
        .join(
            Sale,
            Sale.id == SaleItem.sale_id
        )
        .filter(
            Sale.company_id == company_id
        )
    )

    query = apply_date_filter(
        query,
        date_from,
        date_to,
    )

    data = (
        query
        .group_by(
            Product.id,
            Product.name
        )
        .order_by(order_column)
        .limit(10)
        .all()
    )

    return [
        {
            "product_name": row.product_name,
            "quantity_sold": int(row.quantity_sold),
            "revenue": float(row.revenue),
        }
        for row in data
    ]

def get_top_categories(
    db: Session,
    company_id: int,
    date_from=None,
    date_to=None,
):
    """
    Top Performing Categories by Revenue
    """

    query = (
        db.query(
            Category.name.label("category_name"),
            func.coalesce(
                func.sum(SaleItem.total),
                0
            ).label("revenue"),
        )
        .join(
            Product,
            Product.category_id == Category.id
        )
        .join(
            SaleItem,
            SaleItem.product_id == Product.id
        )
        .join(
            Sale,
            Sale.id == SaleItem.sale_id
        )
        .filter(
            Sale.company_id == company_id
        )
    )

    query = apply_date_filter(
        query,
        date_from,
        date_to,
    )

    data = (
        query
        .group_by(
            Category.id,
            Category.name
        )
        .order_by(
            func.coalesce(
                func.sum(SaleItem.total),
                0
            ).desc()
        )
        .all()
    )

    return [
        {
            "category_name": row.category_name,
            "revenue": float(row.revenue),
        }
        for row in data
    ]

def get_payment_method_analysis(
    db: Session,
    company_id: int,
    date_from=None,
    date_to=None,
):
    """
    Sales distribution by payment method.
    """

    query = (
        db.query(
            Sale.payment_method,
            func.count(Sale.id).label("transaction_count"),
            func.coalesce(
                func.sum(Sale.total_amount),
                0
            ).label("total_sales"),
        )
        .filter(
            Sale.company_id == company_id
        )
    )

    query = apply_date_filter(
        query,
        date_from,
        date_to,
    )

    data = (
        query
        .group_by(
            Sale.payment_method
        )
        .order_by(
            func.sum(Sale.total_amount).desc()
        )
        .all()
    )

    return [
        {
            "payment_method": row.payment_method,
            "transaction_count": int(row.transaction_count),
            "total_sales": float(row.total_sales),
        }
        for row in data
    ]
def get_sales_channel_analysis(
    db: Session,
    company_id: int,
    date_from=None,
    date_to=None,
):
    """
    Sales by Sales Channel
    """

    query = (
        db.query(
            Sale.sales_channel,
            func.coalesce(
                func.sum(Sale.total_amount),
                0
            ).label("total_sales"),
        )
        .filter(
            Sale.company_id == company_id
        )
    )

    query = apply_date_filter(
        query,
        date_from,
        date_to,
    )

    data = (
        query
        .group_by(
            Sale.sales_channel
        )
        .order_by(
            func.coalesce(
                func.sum(Sale.total_amount),
                0
            ).desc()
        )
        .all()
    )

    return [
        {
            "sales_channel": row.sales_channel,
            "total_sales": float(row.total_sales),
        }
        for row in data
    ]

def get_inventory_by_category(
    db: Session,
    company_id: int,
):
    """
    Inventory Distribution by Category
    """

    data = (
        db.query(
            Category.name.label("category_name"),
            func.coalesce(
                func.sum(Inventory.available_stock),
                0
            ).label("stock"),
        )
        .join(
            Product,
            Product.category_id == Category.id
        )
        .join(
            Inventory,
            Inventory.product_id == Product.id
        )
        .filter(
            Inventory.company_id == company_id
        )
        .group_by(
            Category.id,
            Category.name
        )
        .order_by(
            Category.name
        )
        .all()
    )

    return [
        {
            "category_name": row.category_name,
            "stock": int(row.stock),
        }
        for row in data
    ]
def get_stock_status_summary(
    db: Session,
    company_id: int,
):
    """
    Stock Status Summary
    """

    data = (
        db.query(
            Inventory.stock_status,
            func.count(Inventory.id).label("total_products"),
        )
        .filter(
            Inventory.company_id == company_id
        )
        .group_by(
            Inventory.stock_status
        )
        .order_by(
            Inventory.stock_status
        )
        .all()
    )

    return [
        {
            "stock_status": row.stock_status,
            "total_products": int(row.total_products),
        }
        for row in data
    ]

def get_inventory_value_by_category(
    db: Session,
    company_id: int,
):
    """
    Inventory Value by Category
    """

    data = (
        db.query(
            Category.name.label("category_name"),
            func.coalesce(
                func.sum(
                    Inventory.available_stock * Product.unit_price
                ),
                0,
            ).label("inventory_value"),
        )
        .join(
            Product,
            Product.category_id == Category.id
        )
        .join(
            Inventory,
            Inventory.product_id == Product.id
        )
        .filter(
            Inventory.company_id == company_id
        )
        .group_by(
            Category.id,
            Category.name
        )
        .order_by(
            func.coalesce(
                func.sum(
                    Inventory.available_stock * Product.unit_price
                ),
                0
            ).desc()
        )
        .all()
    )

    return [
        {
            "category_name": row.category_name,
            "inventory_value": float(row.inventory_value),
        }
        for row in data
    ]

def get_sales_summary(
    db: Session,
    company_id: int,
    date_from=None,
    date_to=None,
):
    """
    Sales Analytics Summary
    """

    # Total Revenue
    revenue_query = (
        db.query(
            func.coalesce(func.sum(Sale.total_amount), 0)
        )
        .filter(Sale.company_id == company_id)
    )

    revenue_query = apply_date_filter(
        revenue_query,
        date_from,
        date_to,
    )

    total_revenue = revenue_query.scalar()

    # Total Orders
    orders_query = (
        db.query(func.count(Sale.id))
        .filter(Sale.company_id == company_id)
    )

    orders_query = apply_date_filter(
        orders_query,
        date_from,
        date_to,
    )

    total_orders = orders_query.scalar()

    # Average Order Value
    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    # Total Items Sold
    items_query = (
        db.query(
            func.coalesce(func.sum(SaleItem.quantity), 0)
        )
        .join(
            Sale,
            Sale.id == SaleItem.sale_id
        )
        .filter(Sale.company_id == company_id)
    )

    items_query = apply_date_filter(
        items_query,
        date_from,
        date_to,
    )

    total_items_sold = items_query.scalar()

    # Total Discount
    discount_query = (
        db.query(
            func.coalesce(func.sum(Sale.discount), 0)
        )
        .filter(Sale.company_id == company_id)
    )

    discount_query = apply_date_filter(
        discount_query,
        date_from,
        date_to,
    )

    total_discount = discount_query.scalar()

    # Total Tax
    tax_query = (
        db.query(
            func.coalesce(func.sum(Sale.tax), 0)
        )
        .filter(Sale.company_id == company_id)
    )

    tax_query = apply_date_filter(
        tax_query,
        date_from,
        date_to,
    )

    total_tax = tax_query.scalar()

    return SalesSummaryResponse(
        total_revenue=float(total_revenue or 0),
        total_orders=int(total_orders or 0),
        average_order_value=round(
            float(average_order_value or 0),
            2
        ),
        total_items_sold=int(total_items_sold or 0),
        total_discount=float(total_discount or 0),
        total_tax=float(total_tax or 0),
    )

def get_sales_vs_orders(
    db: Session,
    company_id: int,
    period: str = "daily",
    date_from=None,
    date_to=None,
):
    """
    Revenue vs order count by daily, weekly, or monthly period.
    """

    if period not in ["daily", "weekly", "monthly"]:
        raise ValueError(
            "Period must be daily, weekly, or monthly"
        )

    if period == "daily":
        date_group = cast(
            Sale.sale_date,
            Date
        )

    elif period == "weekly":
        date_group = func.date_trunc(
            "week",
            Sale.sale_date
        )

    else:
        date_group = func.date_trunc(
            "month",
            Sale.sale_date
        )

    query = (
        db.query(
            date_group.label("date"),
            func.coalesce(
                func.sum(Sale.total_amount),
                0
            ).label("revenue"),
            func.count(Sale.id).label("orders"),
        )
        .filter(
            Sale.company_id == company_id
        )
    )

    query = apply_date_filter(
        query,
        date_from,
        date_to,
    )

    data = (
        query
        .group_by(date_group)
        .order_by(date_group)
        .all()
    )

    return [
        {
            "date": str(row.date.date())
            if hasattr(row.date, "date")
            else str(row.date),
            "revenue": float(row.revenue),
            "orders": int(row.orders),
        }
        for row in data
    ]

def get_top_customers(
    db: Session,
    company_id: int,
    date_from=None,
    date_to=None,
):
    """
    Top customers ranked by total revenue.
    """

    query = (
        db.query(
            Sale.customer_name.label("customer_name"),
            func.count(Sale.id).label("orders"),
            func.coalesce(
                func.sum(Sale.total_amount),
                0
            ).label("total_spend"),
            func.coalesce(
                func.avg(Sale.total_amount),
                0
            ).label("average_order_value"),
        )
        .filter(
            Sale.company_id == company_id
        )
    )

    query = apply_date_filter(
        query,
        date_from,
        date_to,
    )

    data = (
        query
        .group_by(
            Sale.customer_id,
            Sale.customer_name,
        )
        .order_by(
            func.sum(Sale.total_amount).desc()
        )
        .limit(10)
        .all()
    )

    return [
        {
            "customer_name": row.customer_name,
            "orders": int(row.orders),
            "total_spend": float(row.total_spend),
            "average_order_value": round(
                float(row.average_order_value),
                2
            ),
        }
        for row in data
    ]