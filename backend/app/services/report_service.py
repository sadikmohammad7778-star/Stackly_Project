import json
from datetime import timedelta
from math import ceil

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product
from app.models.category import Category
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.report_history import ReportHistory

from app.schemas.report_schema import (
    ReportFilters,
    SalesReport,
    StockReport,
    SalesReportItem,
    SalesReportResponse,
    InventoryReportItem,
    InventoryReportResponse,
    CustomerReportItem,
    CustomerReportResponse,
    ProductPerformanceItem,
    ProductPerformanceResponse,
    StockMovementItem,
    StockMovementReportResponse,
)


def get_total_pages(total_records, page_size):
    if total_records == 0:
        return 0

    return ceil(total_records / page_size)


def apply_date_filter(query, column, start_date, end_date):
    if start_date:
        query = query.filter(
            column >= start_date
        )

    if end_date:
        query = query.filter(
            column < end_date + timedelta(days=1)
        )

    return query


def get_sales_report(
    db: Session,
    company_id: int,
):
    total_sales = (
        db.query(Sale)
        .filter(
            Sale.company_id == company_id
        )
        .count()
    )

    total_revenue = (
        db.query(
            func.sum(Sale.total_amount)
        )
        .filter(
            Sale.company_id == company_id
        )
        .scalar()
        or 0
    )

    average_order_value = (
        total_revenue / total_sales
        if total_sales > 0
        else 0
    )

    return SalesReport(
        total_sales=total_sales,
        total_revenue=float(total_revenue),
        average_order_value=float(
            average_order_value
        ),
    )


def get_stock_report(
    db: Session,
    company_id: int,
):
    total_products = (
        db.query(Product)
        .filter(
            Product.company_id == company_id
        )
        .count()
    )

    in_stock = (
        db.query(Inventory)
        .filter(
            Inventory.company_id == company_id,
            Inventory.stock_status == "In Stock",
        )
        .count()
    )

    low_stock = (
        db.query(Inventory)
        .filter(
            Inventory.company_id == company_id,
            Inventory.stock_status == "Low Stock",
        )
        .count()
    )

    out_of_stock = (
        db.query(Inventory)
        .filter(
            Inventory.company_id == company_id,
            Inventory.stock_status == "Out of Stock",
        )
        .count()
    )

    return StockReport(
        total_products=total_products,
        in_stock=in_stock,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
    )


def get_sales_report_data(
    db: Session,
    company_id: int,
    filters: ReportFilters,
):
    query = (
        db.query(Sale)
        .filter(
            Sale.company_id == company_id
        )
    )

    if (
        filters.product_id
        or filters.category_id
        or filters.brand
    ):
        query = (
            query
            .join(
                SaleItem,
                SaleItem.sale_id == Sale.id,
            )
            .join(
                Product,
                Product.id == SaleItem.product_id,
            )
        )

        if filters.product_id:
            query = query.filter(
                SaleItem.product_id
                == filters.product_id
            )

        if filters.category_id:
            query = query.filter(
                SaleItem.category_id
                == filters.category_id
            )

        if filters.brand:
            query = query.filter(
                Product.brand.ilike(
                    f"%{filters.brand}%"
                )
            )

    if filters.customer_id:
        query = query.filter(
            Sale.customer_id
            == filters.customer_id
        )

    if filters.sales_status:
        query = query.filter(
            Sale.status
            == filters.sales_status
        )

    query = apply_date_filter(
        query,
        Sale.sale_date,
        filters.start_date,
        filters.end_date,
    )

    query = query.distinct()

    total_records = query.count()

    sort_fields = {
        "sale_date": Sale.sale_date,
        "total_amount": Sale.total_amount,
        "customer_name": Sale.customer_name,
        "status": Sale.status,
        "invoice_number": Sale.invoice_number,
    }

    sort_column = sort_fields.get(
        filters.sort_by,
        Sale.sale_date,
    )

    if filters.sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (
        filters.page - 1
    ) * filters.page_size

    sales = (
        query
        .offset(offset)
        .limit(filters.page_size)
        .all()
    )

    data = [
        SalesReportItem(
            id=sale.id,
            invoice_number=sale.invoice_number,
            customer_id=sale.customer_id,
            customer_name=sale.customer_name,
            sale_date=sale.sale_date,
            sales_channel=sale.sales_channel,
            payment_method=sale.payment_method,
            discount=float(
                sale.discount or 0
            ),
            tax=float(
                sale.tax or 0
            ),
            total_amount=float(
                sale.total_amount or 0
            ),
            status=sale.status,
        )
        for sale in sales
    ]

    return SalesReportResponse(
        report_name="Sales Report",
        total_records=total_records,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=get_total_pages(
            total_records,
            filters.page_size,
        ),
        filters=filters,
        data=data,
    )


def get_inventory_report_data(
    db: Session,
    company_id: int,
    filters: ReportFilters,
):
    query = (
        db.query(
            Inventory,
            Product,
            Category,
        )
        .join(
            Product,
            Product.id == Inventory.product_id,
        )
        .join(
            Category,
            Category.id == Product.category_id,
        )
        .filter(
            Inventory.company_id == company_id,
            Product.company_id == company_id,
            Category.company_id == company_id,
        )
    )

    if filters.product_id:
        query = query.filter(
            Product.id
            == filters.product_id
        )

    if filters.category_id:
        query = query.filter(
            Product.category_id
            == filters.category_id
        )

    if filters.brand:
        query = query.filter(
            Product.brand.ilike(
                f"%{filters.brand}%"
            )
        )

    if filters.stock_status:
        query = query.filter(
            Inventory.stock_status
            == filters.stock_status
        )

    query = apply_date_filter(
        query,
        Inventory.updated_at,
        filters.start_date,
        filters.end_date,
    )

    total_records = query.count()

    sort_fields = {
        "current_stock":
            Inventory.current_stock,
        "available_stock":
            Inventory.available_stock,
        "reorder_level":
            Inventory.reorder_level,
        "product_name":
            Product.name,
        "brand":
            Product.brand,
        "updated_at":
            Inventory.updated_at,
    }

    sort_column = sort_fields.get(
        filters.sort_by,
        Inventory.updated_at,
    )

    if filters.sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (
        filters.page - 1
    ) * filters.page_size

    rows = (
        query
        .offset(offset)
        .limit(filters.page_size)
        .all()
    )

    data = [
        InventoryReportItem(
            id=inventory.id,
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            brand=product.brand,
            category_id=category.id,
            category_name=category.name,
            current_stock=inventory.current_stock,
            reserved_stock=inventory.reserved_stock,
            available_stock=inventory.available_stock,
            reorder_level=inventory.reorder_level,
            stock_status=inventory.stock_status,
        )
        for inventory, product, category in rows
    ]

    return InventoryReportResponse(
        report_name="Inventory Report",
        total_records=total_records,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=get_total_pages(
            total_records,
            filters.page_size,
        ),
        filters=filters,
        data=data,
    )


def get_customer_report_data(
    db: Session,
    company_id: int,
    filters: ReportFilters,
):
    query = (
        db.query(Customer)
        .filter(
            Customer.company_id
            == company_id
        )
    )

    if filters.customer_id:
        query = query.filter(
            Customer.id
            == filters.customer_id
        )

    if filters.start_date:
        query = query.filter(
            Customer.last_purchase_date
            >= filters.start_date
        )

    if filters.end_date:
        query = query.filter(
            Customer.last_purchase_date
            < filters.end_date
            + timedelta(days=1)
        )

    total_records = query.count()

    sort_fields = {
        "total_orders":
            Customer.total_orders,
        "total_spend":
            Customer.total_spend,
        "last_purchase_date":
            Customer.last_purchase_date,
        "first_name":
            Customer.first_name,
        "last_name":
            Customer.last_name,
        "created_at":
            Customer.created_at,
    }

    sort_column = sort_fields.get(
        filters.sort_by,
        Customer.created_at,
    )

    if filters.sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (
        filters.page - 1
    ) * filters.page_size

    customers = (
        query
        .offset(offset)
        .limit(filters.page_size)
        .all()
    )

    data = [
        CustomerReportItem(
            id=customer.id,
            customer_id=customer.customer_id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            segment=customer.segment,
            status=customer.status,
            total_orders=customer.total_orders,
            total_spend=float(
                customer.total_spend or 0
            ),
            last_purchase_date=
                customer.last_purchase_date,
        )
        for customer in customers
    ]

    return CustomerReportResponse(
        report_name="Customer Report",
        total_records=total_records,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=get_total_pages(
            total_records,
            filters.page_size,
        ),
        filters=filters,
        data=data,
    )


def get_product_performance_report_data(
    db: Session,
    company_id: int,
    filters: ReportFilters,
):
    query = (
        db.query(
            Product.id.label(
                "product_id"
            ),
            Product.name.label(
                "product_name"
            ),
            Product.sku.label("sku"),
            Product.brand.label("brand"),
            Category.id.label(
                "category_id"
            ),
            Category.name.label(
                "category_name"
            ),
            func.coalesce(
                func.sum(
                    SaleItem.quantity
                ),
                0,
            ).label(
                "total_quantity_sold"
            ),
            func.coalesce(
                func.sum(
                    SaleItem.total
                ),
                0,
            ).label(
                "total_sales"
            ),
            func.count(
                func.distinct(Sale.id)
            ).label(
                "total_orders"
            ),
        )
        .join(
            SaleItem,
            SaleItem.product_id
            == Product.id,
        )
        .join(
            Sale,
            Sale.id
            == SaleItem.sale_id,
        )
        .join(
            Category,
            Category.id
            == Product.category_id,
        )
        .filter(
            Product.company_id
            == company_id,
            Sale.company_id
            == company_id,
            Category.company_id
            == company_id,
        )
    )

    if filters.product_id:
        query = query.filter(
            Product.id
            == filters.product_id
        )

    if filters.category_id:
        query = query.filter(
            Product.category_id
            == filters.category_id
        )

    if filters.brand:
        query = query.filter(
            Product.brand.ilike(
                f"%{filters.brand}%"
            )
        )

    if filters.customer_id:
        query = query.filter(
            Sale.customer_id
            == filters.customer_id
        )

    if filters.sales_status:
        query = query.filter(
            Sale.status
            == filters.sales_status
        )

    query = apply_date_filter(
        query,
        Sale.sale_date,
        filters.start_date,
        filters.end_date,
    )

    query = query.group_by(
        Product.id,
        Product.name,
        Product.sku,
        Product.brand,
        Category.id,
        Category.name,
    )

    grouped_query = query.subquery()

    total_records = (
        db.query(
            func.count()
        )
        .select_from(grouped_query)
        .scalar()
        or 0
    )

    sort_fields = {
        "product_name":
            grouped_query.c.product_name,
        "brand":
            grouped_query.c.brand,
        "total_quantity_sold":
            grouped_query.c.total_quantity_sold,
        "total_sales":
            grouped_query.c.total_sales,
        "total_orders":
            grouped_query.c.total_orders,
    }

    sort_column = sort_fields.get(
        filters.sort_by,
        grouped_query.c.total_sales,
    )

    if filters.sort_order == "asc":
        sort_expression = (
            sort_column.asc()
        )
    else:
        sort_expression = (
            sort_column.desc()
        )

    offset = (
        filters.page - 1
    ) * filters.page_size

    rows = (
        db.query(grouped_query)
        .order_by(sort_expression)
        .offset(offset)
        .limit(filters.page_size)
        .all()
    )

    data = [
        ProductPerformanceItem(
            product_id=row.product_id,
            product_name=row.product_name,
            sku=row.sku,
            brand=row.brand,
            category_id=row.category_id,
            category_name=row.category_name,
            total_quantity_sold=int(
                row.total_quantity_sold or 0
            ),
            total_sales=float(
                row.total_sales or 0
            ),
            total_orders=int(
                row.total_orders or 0
            ),
        )
        for row in rows
    ]

    return ProductPerformanceResponse(
        report_name=
            "Product Performance Report",
        total_records=total_records,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=get_total_pages(
            total_records,
            filters.page_size,
        ),
        filters=filters,
        data=data,
    )


def get_stock_movement_report_data(
    db: Session,
    company_id: int,
    filters: ReportFilters,
):
    query = (
        db.query(
            InventoryMovement,
            Inventory,
            Product,
        )
        .join(
            Inventory,
            Inventory.id
            == InventoryMovement.inventory_id,
        )
        .join(
            Product,
            Product.id
            == Inventory.product_id,
        )
        .filter(
            Inventory.company_id
            == company_id,
            Product.company_id
            == company_id,
        )
    )

    if filters.product_id:
        query = query.filter(
            Product.id
            == filters.product_id
        )

    if filters.category_id:
        query = query.filter(
            Product.category_id
            == filters.category_id
        )

    if filters.brand:
        query = query.filter(
            Product.brand.ilike(
                f"%{filters.brand}%"
            )
        )

    if filters.stock_status:
        query = query.filter(
            Inventory.stock_status
            == filters.stock_status
        )

    query = apply_date_filter(
        query,
        InventoryMovement.created_at,
        filters.start_date,
        filters.end_date,
    )

    total_records = query.count()

    sort_fields = {
        "created_at":
            InventoryMovement.created_at,
        "quantity_changed":
            InventoryMovement.quantity_changed,
        "movement_type":
            InventoryMovement.movement_type,
        "product_name":
            Product.name,
    }

    sort_column = sort_fields.get(
        filters.sort_by,
        InventoryMovement.created_at,
    )

    if filters.sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    offset = (
        filters.page - 1
    ) * filters.page_size

    rows = (
        query
        .offset(offset)
        .limit(filters.page_size)
        .all()
    )

    data = [
        StockMovementItem(
            id=movement.id,
            inventory_id=inventory.id,
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            movement_type=movement.movement_type,
            quantity_changed=
                movement.quantity_changed,
            previous_quantity=
                movement.previous_quantity,
            updated_quantity=
                movement.updated_quantity,
            reason=movement.reason,
            remarks=movement.remarks,
            performed_by=movement.performed_by,
            created_at=movement.created_at,
        )
        for movement, inventory, product in rows
    ]

    return StockMovementReportResponse(
        report_name=
            "Stock Movement Report",
        total_records=total_records,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=get_total_pages(
            total_records,
            filters.page_size,
        ),
        filters=filters,
        data=data,
    )


def create_report_history(
    db: Session,
    company_id: int,
    user_id: int,
    report_name: str,
    filters: ReportFilters | None,
    report_format: str,
    status: str = "Success",
    error_message: str | None = None,
    file_path: str | None = None,
):
    history = ReportHistory(
        company_id=company_id,
        generated_by=user_id,
        report_name=report_name,
        filters=json.dumps(
            filters.model_dump(mode="json")
            if filters
            else {}
        ),
        format=report_format,
        status=status,
        error_message=error_message,
        file_path=file_path,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


def get_report_history(
    db: Session,
    company_id: int,
    page: int = 1,
    page_size: int = 20,
):
    query = (
        db.query(ReportHistory)
        .filter(
            ReportHistory.company_id
            == company_id
        )
        .order_by(
            ReportHistory.generated_at.desc()
        )
    )

    total_records = query.count()

    histories = (
        query
        .offset(
            (page - 1) * page_size
        )
        .limit(page_size)
        .all()
    )

    return {
        "total_records": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": get_total_pages(
            total_records,
            page_size,
        ),
        "data": histories,
    }


def get_report_history_by_id(
    db: Session,
    company_id: int,
    history_id: int,
):
    return (
        db.query(ReportHistory)
        .filter(
            ReportHistory.id == history_id,
            ReportHistory.company_id
            == company_id,
        )
        .first()
    )