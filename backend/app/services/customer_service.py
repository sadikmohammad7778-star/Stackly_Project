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
    ip_address: str = None,
    user_agent: str = None,
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
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone,
        address=customer.address,
        city=customer.city,
        state=customer.state,
        country=customer.country,
        postal_code=customer.postal_code,
        segment=customer.segment,
        status=customer.status,
    )

    db.add(new_customer)
    db.flush()

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

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Customers",
        action="CREATE",
        resource_type="Customer",
        resource_id=str(new_customer.id),
        description=(
            f"Customer '{new_customer.first_name} "
            f"{new_customer.last_name}' created."
        ),
        ip_address=ip_address,
        user_agent=user_agent,
        after_values={
            "customer_id": new_customer.customer_id,
            "first_name": new_customer.first_name,
            "last_name": new_customer.last_name,
            "email": new_customer.email,
            "phone": new_customer.phone,
            "address": new_customer.address,
            "city": new_customer.city,
            "state": new_customer.state,
            "country": new_customer.country,
            "postal_code": new_customer.postal_code,
            "segment": new_customer.segment,
            "status": new_customer.status,
        },
        status="SUCCESS",
    )

    create_notification(
        db=db,
        title="New Customer",
        message=(
            f"{new_customer.first_name} "
            f"{new_customer.last_name} has been registered successfully."
        ),
        type="success",
    )

    db.commit()
    db.refresh(new_customer)

    return new_customer

def get_all_customers(
    db: Session,
    company_id: int,
):
    return (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
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
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if not customer:
        raise ValueError("Customer not found.")

    # -----------------------------------
    # Purchase Summary from Sales
    # -----------------------------------

    sales = (
        db.query(Sale)
        .filter(
            Sale.customer_id == customer.id,
            Sale.company_id == company_id,
        )
        .order_by(Sale.sale_date.asc())
        .all()
    )

    total_orders = len(sales)

    total_revenue = sum(
        float(sale.total_amount or 0)
        for sale in sales
    )

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    first_purchase_date = (
        sales[0].sale_date
        if sales
        else None
    )

    last_purchase_date = (
        sales[-1].sale_date
        if sales
        else None
    )

    # -----------------------------------
    # Purchase Frequency
    # -----------------------------------

    purchase_frequency = total_orders

    # -----------------------------------
    # Build response
    # -----------------------------------

    response = {
        "id": customer.id,
        "company_id": customer.company_id,
        "customer_id": customer.customer_id,

        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,

        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "country": customer.country,
        "postal_code": customer.postal_code,

        "segment": customer.segment,
        "status": customer.status,

        "total_orders": total_orders,
        "total_spend": total_revenue,
        "last_purchase_date": last_purchase_date,

        "created_at": customer.created_at,
        "updated_at": customer.updated_at,

        "purchase_summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "average_order_value": average_order_value,
            "total_products_purchased": 0,
            "purchase_frequency": purchase_frequency,
            "first_purchase_date": first_purchase_date,
            "last_purchase_date": last_purchase_date,
        },
    }

    return response

def get_customer_model_by_id(
    db: Session,
    customer_id: int,
    company_id: int,
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if not customer:
        raise ValueError("Customer not found.")

    return customer

# ============================================================
# UPDATE CUSTOMER
# ============================================================

def update_customer(
    db: Session,
    customer_id: int,
    customer: CustomerUpdate,
    company_id: int,
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    existing_customer = get_customer_model_by_id(
        db=db,
        customer_id=customer_id,
        company_id=company_id,
    )

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

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
            raise ValueError(
                "Email already exists."
            )

    # --------------------------------------------------------
    # Check duplicate phone
    # --------------------------------------------------------

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
            raise ValueError(
                "Phone number already exists."
            )

    # --------------------------------------------------------
    # Capture BEFORE values
    # --------------------------------------------------------

    before_values = {
        "customer_id": existing_customer.customer_id,
        "first_name": existing_customer.first_name,
        "last_name": existing_customer.last_name,
        "email": existing_customer.email,
        "phone": existing_customer.phone,
        "address": existing_customer.address,
        "city": existing_customer.city,
        "state": existing_customer.state,
        "country": existing_customer.country,
        "postal_code": existing_customer.postal_code,
        "segment": existing_customer.segment,
        "status": existing_customer.status,
    }

    # --------------------------------------------------------
    # Update customer
    # --------------------------------------------------------

    update_data = customer.model_dump(
        exclude_unset=True
    )

    # Prevent company/user controlled fields
    update_data.pop("company_id", None)
    update_data.pop("created_by", None)
    update_data.pop("user_id", None)

    for key, value in update_data.items():
        setattr(
            existing_customer,
            key,
            value,
        )

    # --------------------------------------------------------
    # Capture AFTER values
    # --------------------------------------------------------

    after_values = {
        "customer_id": existing_customer.customer_id,
        "first_name": existing_customer.first_name,
        "last_name": existing_customer.last_name,
        "email": existing_customer.email,
        "phone": existing_customer.phone,
        "address": existing_customer.address,
        "city": existing_customer.city,
        "state": existing_customer.state,
        "country": existing_customer.country,
        "postal_code": existing_customer.postal_code,
        "segment": existing_customer.segment,
        "status": existing_customer.status,
    }

    # --------------------------------------------------------
    # Create Audit Log
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Customers",
        action="UPDATE",
        resource_type="Customer",
        resource_id=str(
            existing_customer.id
        ),
        description=(
            f"Customer "
            f"'{existing_customer.first_name} "
            f"{existing_customer.last_name}' "
            f"updated."
        ),
        ip_address=ip_address,
        user_agent=user_agent,
        before_values=before_values,
        after_values=after_values,
        status="SUCCESS",
    )

    # --------------------------------------------------------
    # Commit
    # --------------------------------------------------------

    db.commit()

    db.refresh(existing_customer)

    return existing_customer
def delete_customer(
    db: Session,
    customer_id: int,
    company_id: int,
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    customer = get_customer_model_by_id(
        db=db,
        customer_id=customer_id,
        company_id=company_id,
    )

    customer_name = (
        f"{customer.first_name} "
        f"{customer.last_name}"
    )

    # --------------------------------------------------------
    # Capture BEFORE values
    # --------------------------------------------------------

    before_values = {
        "customer_id": customer.customer_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "country": customer.country,
        "postal_code": customer.postal_code,
        "segment": customer.segment,
        "status": customer.status,
    }

    # --------------------------------------------------------
    # Soft Delete
    # --------------------------------------------------------

    customer.deleted_at = datetime.utcnow()

    # --------------------------------------------------------
    # Capture AFTER values
    # --------------------------------------------------------

    after_values = {
        "customer_id": customer.customer_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "country": customer.country,
        "postal_code": customer.postal_code,
        "segment": customer.segment,
        "status": customer.status,
        "deleted_at": customer.deleted_at.isoformat(),
    }

    # --------------------------------------------------------
    # Create Audit Log
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Customers",
        action="DELETE",
        resource_type="Customer",
        resource_id=str(customer.id),
        description=(
            f"Customer '{customer_name}' deleted."
        ),
        ip_address=ip_address,
        user_agent=user_agent,
        before_values=before_values,
        after_values=after_values,
        status="SUCCESS",
    )

    # --------------------------------------------------------
    # Commit
    # --------------------------------------------------------

    db.commit()

    return {
        "message": "Customer deleted successfully."
    }
def change_customer_status(
    db: Session,
    customer_id: int,
    status: str,
    company_id: int,
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    customer = get_customer_by_id(
        db=db,
        customer_id=customer_id,
        company_id=company_id,
    )

    old_status = customer.status

    customer.status = status

    create_audit_log(
        db=db,
        company_id=company_id,
        user_id=user_id,
        module="Customers",
        action="STATUS CHANGE",
        resource_type="Customer",
        resource_id=str(customer.id),
        description=(
            f"Customer '{customer.first_name} "
            f"{customer.last_name}' status changed "
            f"from {old_status} to {status}."
        ),
        ip_address=ip_address,
        user_agent=user_agent,
        before_values={
            "status": old_status,
        },
        after_values={
            "status": status,
        },
        status="SUCCESS",
    )

    db.commit()
    db.refresh(customer)

    customer_name = (
        f"{customer.first_name} "
        f"{customer.last_name}"
    )

    if status == "Inactive":
        create_notification(
            db=db,
            title="Customer Deactivated",
            message=(
                f"{customer_name} has been deactivated."
            ),
            type="warning",
        )

    elif status == "Active":
        create_notification(
            db=db,
            title="Customer Activated",
            message=(
                f"{customer_name} has been activated."
            ),
            type="success",
        )

    return customer

def filter_customers(
    db: Session,
    company_id: int,
    segment: str = None,
    status: str = None,
    city: str = None,
    state: str = None,
    country: str = None,
):

    query = db.query(Customer).filter(
        Customer.company_id == company_id,
        Customer.deleted_at.is_(None),
    )

    if segment:
        query = query.filter(
            Customer.segment == segment
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
            Customer.deleted_at.is_(None),
            or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
                Customer.customer_id.ilike(f"%{search}%"),
            )
        )
        .order_by(Customer.created_at.desc())
        .all()
    )
def get_customer_dashboard(db: Session, company_id: int):

    total_customers = (
        db.query(func.count(Customer.id))
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
        .scalar()
    )

    active_customers = (
        db.query(func.count(Customer.id))
        .filter(
            Customer.company_id == company_id,
            Customer.status == "Active",
            Customer.deleted_at.is_(None),
        )
        .scalar()
    )

    current_month = datetime.now().month
    current_year = datetime.now().year

    new_customers = (
        db.query(func.count(Customer.id))
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
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
            Customer.deleted_at.is_(None),
            CustomerPurchaseSummary.total_orders > 1,
        )
        .scalar()
    )

    total_revenue = (
        db.query(
            func.coalesce(func.sum(Customer.total_spend), 0)
        )
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
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
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
        .scalar()
    ) or 0

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "new_customers": new_customers,
        "returning_customers": returning_customers,
        "average_customer_spend": round(average_spend, 2),
        "total_revenue_generated": float(total_revenue or 0),
        "average_purchase_frequency": round(
            average_purchase_frequency,
            2,
        ),
    }


def get_top_customers(
    db: Session,
    company_id: int,
):
    customers = (
        db.query(
            Customer.first_name,
            Customer.last_name,
            func.coalesce(
                func.sum(Sale.total_amount),
                0
            ).label("revenue"),
        )
        .join(
            Sale,
            Sale.customer_id == Customer.id,
        )
        .filter(
            Customer.company_id == company_id,
            Sale.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
        .group_by(
            Customer.id,
            Customer.first_name,
            Customer.last_name,
        )
        .order_by(
            func.sum(Sale.total_amount).desc()
        )
        .limit(10)
        .all()
    )

    return [
        {
            "name": f"{row.first_name} {row.last_name}",
            "revenue": float(row.revenue or 0),
        }
        for row in customers
    ]

def get_revenue_by_segment(
    db: Session,
    company_id: int,
):
    revenue = (
        db.query(
            Customer.segment.label("segment"),
            func.sum(Sale.total_amount).label("revenue"),
        )
        .join(
            Sale,
            Sale.customer_id == Customer.id,
        )
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
            Sale.company_id == company_id,
        )
        .group_by(Customer.segment)
        .order_by(
            func.sum(Sale.total_amount).desc()
        )
        .all()
    )

    return [
        {
            "segment": row.segment or "Unknown",
            "revenue": float(row.revenue or 0),
        }
        for row in revenue
    ]
def get_customer_growth(
    db: Session,
    company_id: int,
):
    growth = (
        db.query(
            func.date_trunc(
                "month",
                Customer.created_at
            ).label("month"),
            func.count(Customer.id).label("customers"),
        )
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
        .group_by(
            func.date_trunc(
                "month",
                Customer.created_at
            )
        )
        .order_by(
            func.date_trunc(
                "month",
                Customer.created_at
            )
        )
        .all()
    )

    return [
        {
            "month": row.month.strftime("%b %Y"),
            "customers": int(row.customers),
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
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
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
    # Check customer exists
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if not customer:
        raise ValueError("Customer not found.")

    # Get customer's sales
    sales = (
        db.query(Sale)
        .filter(
            Sale.customer_id == customer_id,
            Sale.company_id == company_id,
        )
        .order_by(
            Sale.sale_date.desc()
        )
        .all()
    )

    return [
        {
            "id": sale.id,
            "invoice_number": sale.invoice_number,
            "created_at": sale.sale_date or sale.created_at,
            "total_amount": float(
                sale.total_amount or 0
            ),
            "payment_method": sale.payment_method,
            "sales_channel": sale.sales_channel,
        }
        for sale in sales
    ]

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
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
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
            "First Name",
            "Last Name",
            "Email",
            "Phone",
            "City",
            "State",
            "Country",
            "Segment",
            "Status",
        ])

        for customer in customers:

            writer.writerow([
                customer.customer_id,
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.phone,
                customer.city,
                customer.state,
                customer.country,
                customer.segment,
                customer.status,
            ])

    return file_path

def export_customers_pdf(
    db: Session,
    company_id: int,
):
    customers = (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )
        .all()
    )

    folder = "exports"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, "customers.pdf")

    document = SimpleDocTemplate(file_path)

    data = [
        [
            "Customer ID",
            "Customer Name",
            "Email",
            "Phone",
            "Segment",
            "Status",
        ]
    ]

    for customer in customers:
        data.append([
            customer.customer_id,
            f"{customer.first_name} {customer.last_name}",
            customer.email,
            customer.phone,
            customer.segment,
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


