from sqlalchemy.orm import Session
from sqlalchemy import or_, func, extract,desc

from datetime import datetime

import csv
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
)
from reportlab.lib import colors

from app.models.customer import Customer
from app.models.customer_purchase_summary import CustomerPurchaseSummary
from app.models.customer_timeline import CustomerTimeline
from app.models.sale import Sale
from app.services.notification_service import create_notification
from app.services.audit_service import create_audit_log

from app.schemas.customer_schema import (
    CustomerCreate,
    CustomerUpdate,
)



def generate_customer_id(db: Session):

    last_customer = (
        db.query(Customer)
        .order_by(Customer.id.desc())
        .first()
    )

    if not last_customer:
        return "CUS0001"

    last_number = int(last_customer.customer_id.replace("CUS", ""))

    return f"CUS{last_number + 1:04d}"


def create_customer(
    db: Session,
    customer: CustomerCreate,
    company_id: int,
    user_id: int,
):

    existing_email = (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            Customer.email == customer.email,
        )
        .first()
    )

    if existing_email:
        raise ValueError("Email already exists.")

    existing_phone = (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            Customer.phone == customer.phone,
        )
        .first()
    )

    if existing_phone:
        raise ValueError("Phone already exists.")

    customer_code = generate_customer_id(db)

    new_customer = Customer(
        company_id=company_id,
        customer_id=customer_code,
        full_name=customer.full_name,
        email=customer.email,
        phone=customer.phone,
        gender=customer.gender,
        date_of_birth=customer.date_of_birth,
        address=customer.address,
        city=customer.city,
        state=customer.state,
        country=customer.country,
        customer_type=customer.customer_type,
        preferred_sales_channel=customer.preferred_sales_channel,
        status="Active",
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    summary = CustomerPurchaseSummary(
        customer_id=new_customer.id,
        total_orders=0,
        total_revenue=0,
        total_products_purchased=0,
        average_order_value=0,
        purchase_frequency=0,
    )

    timeline = CustomerTimeline(
        customer_id=new_customer.id,
        event="Customer Registered",
        description="Customer account created.",
    )

    db.add(summary)
    db.add(timeline)

    db.commit()

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Customers",
        action="CREATE",
        description=f"Customer '{new_customer.full_name}' created.",
    )
    create_notification(
        db=db,
        title="New Customer",
        message=f"{new_customer.full_name} has been registered successfully.",
        type="success",
    )

    return new_customer


def get_all_customers(
    db: Session,
    company_id: int,
):
    return (
        db.query(Customer)
        .filter(Customer.company_id == company_id)
        .order_by(Customer.created_at.desc())
        .all()
    )    

def get_customer_by_id(
    db: Session,
    customer_id: int,
    company_id: int,
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == company_id,
        )
        .first()
    )

    if not customer:
        raise ValueError("Customer not found.")

    return customer



def update_customer(
    db: Session,
    customer_id: int,
    customer: CustomerUpdate,
    company_id: int,
    user_id: int,
):
    existing_customer = get_customer_by_id(
        db,
        customer_id,
        company_id,
    )

    if customer.email:
        email_exists = (
            db.query(Customer)
            .filter(
                Customer.company_id == company_id,
                Customer.email == customer.email,
                Customer.id != customer_id,
            )
            .first()
        )

        if email_exists:
            raise ValueError("Email already exists.")

    if customer.phone:
        phone_exists = (
            db.query(Customer)
            .filter(
                Customer.company_id == company_id,
                Customer.phone == customer.phone,
                Customer.id != customer_id,
            )
            .first()
        )

        if phone_exists:
            raise ValueError("Phone number already exists.")

    update_data = customer.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_customer, key, value)

    db.commit()
    db.refresh(existing_customer)

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Customers",
        action="UPDATE",
        description=f"Customer '{existing_customer.full_name}' updated.",
    )

    return existing_customer


def delete_customer(
    db: Session,
    customer_id: int,
    company_id: int,
    user_id: int,
):

    customer = get_customer_by_id(
        db,
        customer_id,
        company_id,
    )

    customer_name = customer.full_name

    db.delete(customer)

    db.commit()

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Customers",
        action="DELETE",
        description=f"Customer '{customer_name}' deleted.",
    )

    return {
        "message": "Customer deleted successfully."
    }

def change_customer_status(
    db: Session,
    customer_id: int,
    status: str,
    company_id: int,
    user_id: int,
):

    customer = get_customer_by_id(
        db,
        customer_id,
        company_id,
    )

    customer.status = status

    db.commit()

    db.refresh(customer)

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Customers",
        action="STATUS CHANGE",
        description=f"Customer '{customer.full_name}' status changed to {status}.",
    )

    if status == "Inactive":

        create_notification(
            db=db,
            title="Customer Deactivated",
            message=f"{customer.full_name} has been deactivated.",
            type="warning",
        )

    elif status == "Active":

        create_notification(
            db=db,
            title="Customer Activated",
            message=f"{customer.full_name} has been activated.",
            type="success",
        )

    return customer

def filter_customers(
    db: Session,
    company_id: int,
    customer_type: str = None,
    status: str = None,
    city: str = None,
    state: str = None,
    country: str = None,
):

    query = db.query(Customer).filter(
        Customer.company_id == company_id
    )

    if customer_type:
        query = query.filter(
            Customer.customer_type == customer_type
        )

    if status:
        query = query.filter(
            Customer.status == status
        )

    if city:
        query = query.filter(
            Customer.city == city
        )

    if state:
        query = query.filter(
            Customer.state == state
        )

    if country:
        query = query.filter(
            Customer.country == country
        )

    return query.order_by(
        Customer.created_at.desc()
    ).all()


def search_customers(
    db: Session,
    search: str,
    company_id: int,
):
    return (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            or_(
                Customer.full_name.ilike(f"%{search}%"),
                Customer.customer_id.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
            ),
        )
        .all()
    )


def get_customer_dashboard(db: Session, company_id: int):

    total_customers = (
        db.query(func.count(Customer.id))
        .filter(Customer.company_id == company_id)
        .scalar()
    )

    active_customers = (
        db.query(func.count(Customer.id))
        .filter(
            Customer.company_id == company_id,
            Customer.status == "Active",
        )
        .scalar()
    )

    current_month = datetime.now().month
    current_year = datetime.now().year

    new_customers = (
        db.query(func.count(Customer.id))
        .filter(
            Customer.company_id == company_id,
            extract("month", Customer.created_at) == current_month,
            extract("year", Customer.created_at) == current_year,
        )
        .scalar()
    )

    returning_customers = (
        db.query(func.count(CustomerPurchaseSummary.id))
        .join(Customer)
        .filter(
            Customer.company_id == company_id,
            CustomerPurchaseSummary.total_orders > 1,
        )
        .scalar()
    )

    total_revenue = (
        db.query(func.coalesce(func.sum(CustomerPurchaseSummary.total_revenue), 0))
        .join(Customer)
        .filter(Customer.company_id == company_id)
        .scalar()
    )

    average_spend = (
        total_revenue / total_customers
        if total_customers
        else 0
    )

    average_purchase_frequency = (
        db.query(func.avg(CustomerPurchaseSummary.purchase_frequency))
        .join(Customer)
        .filter(Customer.company_id == company_id)
        .scalar()
    ) or 0

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "new_customers": new_customers,
        "returning_customers": returning_customers,
        "average_customer_spend": round(average_spend, 2),
        "total_revenue_generated": total_revenue,
        "average_purchase_frequency": round(
            average_purchase_frequency,
            2,
        ),
    }


def get_top_customers(db: Session, company_id: int):

    customers = (
        db.query(
            Customer.full_name,
            CustomerPurchaseSummary.total_revenue,
        )
        .join(CustomerPurchaseSummary)
        .filter(Customer.company_id == company_id)
        .order_by(
            CustomerPurchaseSummary.total_revenue.desc()
        )
        .limit(10)
        .all()
    )

    return [
    {
        "name": row.full_name,
        "revenue": float(row.total_revenue or 0),
    }
    for row in customers
]


def get_revenue_by_customer_type(
    db: Session,
    company_id: int,
):

    revenue = (
        db.query(
            Customer.customer_type,
            func.sum(
                CustomerPurchaseSummary.total_revenue
            ),
        )
        .join(CustomerPurchaseSummary)
        .filter(Customer.company_id == company_id)
        .group_by(Customer.customer_type)
        .all()
    )

    return [
    {
        "customer_type": row.customer_type,
        "sum": float(row[1] or 0),
    }
    for row in revenue
]

def get_customer_growth(
    db: Session,
    company_id: int,
):

    growth = (
        db.query(
            extract("month", Customer.created_at).label("month"),
            func.count(Customer.id).label("customers"),
        )
        .filter(Customer.company_id == company_id)
        .group_by("month")
        .order_by("month")
        .all()
    )

    return [
    {
        "month": int(row.month),
        "customers": row.customers,
    }
    for row in growth
]


def get_customer_distribution(
    db: Session,
    company_id: int,
):

    distribution = (
        db.query(
            Customer.city.label("city"),
            func.count(Customer.id).label("count"),
        )
        .filter(Customer.company_id == company_id)
        .group_by(Customer.city)
        .all()
    )

    return [
        {
            "city": row.city,
            "count": row.count,
        }
        for row in distribution
    ]


def get_customer_purchase_history(
    db: Session,
    customer_id: int,
    company_id: int,
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == company_id,
        )
        .first()
    )

    if not customer:
        raise ValueError("Customer not found.")

    return []

def get_customer_timeline(
    db: Session,
    customer_id: int,
    company_id: int,
):
    customer = get_customer_by_id(
        db,
        customer_id,
        company_id,
    )

    timeline = (
        db.query(CustomerTimeline)
        .filter(
            CustomerTimeline.customer_id == customer.id
        )
        .order_by(
            CustomerTimeline.created_at.desc()
        )
        .all()
    )

    return timeline


def export_customers_csv(
    db: Session,
    company_id: int,
):
    customers = (
        db.query(Customer)
        .filter(Customer.company_id == company_id)
        .all()
    )

    folder = "exports"

    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(
        folder,
        "customers.csv",
    )

    with open(
        file_path,
        mode="w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Customer ID",
            "Full Name",
            "Email",
            "Phone",
            "City",
            "State",
            "Country",
            "Customer Type",
            "Status",
        ])

        for customer in customers:

            writer.writerow([
                customer.customer_id,
                customer.full_name,
                customer.email,
                customer.phone,
                customer.city,
                customer.state,
                customer.country,
                customer.customer_type,
                customer.status,
            ])

    return file_path


def export_customers_pdf(db: Session, company_id: int):
    customers = (
        db.query(Customer)
        .filter(Customer.company_id == company_id)
        .all()
    )

    folder = "exports"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, "customers.pdf")

    document = SimpleDocTemplate(file_path)

    data = [
        [
            "Customer ID",
            "Name",
            "Email",
            "Phone",
            "Customer Type",
            "Status",
        ]
    ]

    for customer in customers:
        data.append([
            customer.customer_id,
            customer.full_name,
            customer.email,
            customer.phone,
            customer.customer_type,
            customer.status,
        ])

    table = Table(data)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ])
    )

    document.build([table])

    return file_path


def calculate_customer_segment(summary):
    if summary.total_orders == 0:
        return "New Customer"

    if summary.total_orders <= 5:
        return "Regular Customer"

    if summary.total_orders <= 10:
        return "Loyal Customer"

    return "VIP Customer"


