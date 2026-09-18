from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


class ReportFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    customer_id: Optional[int] = None
    sales_status: Optional[str] = None
    stock_status: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SalesReport(BaseModel):
    total_sales: int
    total_revenue: float
    average_order_value: float


class StockReport(BaseModel):
    total_products: int
    in_stock: int
    low_stock: int
    out_of_stock: int


class SalesReportItem(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    customer_name: str
    sale_date: datetime
    sales_channel: str
    payment_method: str
    discount: float
    tax: float
    total_amount: float
    status: str


class SalesReportResponse(BaseModel):
    report_name: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    filters: ReportFilters
    data: List[SalesReportItem]


class InventoryReport(BaseModel):
    total_products: int
    in_stock: int
    low_stock: int
    out_of_stock: int


class InventoryReportItem(BaseModel):
    id: int
    product_id: int
    product_name: str
    sku: str
    brand: str
    category_id: int
    category_name: str
    current_stock: int
    reserved_stock: int
    available_stock: int
    reorder_level: int
    stock_status: str


class InventoryReportResponse(BaseModel):
    report_name: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    filters: ReportFilters
    data: List[InventoryReportItem]


class CustomerReportItem(BaseModel):
    id: int
    customer_id: str
    first_name: str
    last_name: str
    email: str
    segment: str
    status: str
    total_orders: int
    total_spend: float
    last_purchase_date: Optional[datetime] = None


class CustomerReportResponse(BaseModel):
    report_name: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    filters: ReportFilters
    data: List[CustomerReportItem]


class ProductPerformanceItem(BaseModel):
    product_id: int
    product_name: str
    sku: str
    brand: str
    category_id: int
    category_name: str
    total_quantity_sold: int
    total_sales: float
    total_orders: int


class ProductPerformanceResponse(BaseModel):
    report_name: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    filters: ReportFilters
    data: List[ProductPerformanceItem]


class StockMovementItem(BaseModel):
    id: int
    inventory_id: int
    product_id: int
    product_name: str
    sku: str
    movement_type: str
    quantity_changed: int
    previous_quantity: int
    updated_quantity: int
    reason: str
    remarks: Optional[str] = None
    performed_by: Optional[int] = None
    created_at: datetime


class StockMovementReportResponse(BaseModel):
    report_name: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    filters: ReportFilters
    data: List[StockMovementItem]


class ReportHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    generated_by: int
    report_name: str
    filters: Optional[str] = None
    format: str
    status: str
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    generated_at: datetime


class ReportHistoryListResponse(BaseModel):
    total_records: int
    page: int
    page_size: int
    total_pages: int
    data: List[ReportHistoryResponse]


class ScheduledReportCreate(BaseModel):
    report_type: str
    filters: Optional[str] = None
    frequency: str
    execution_time: str
    recipients: str
    format: str = "PDF"
    is_active: bool = True


class ScheduledReportUpdate(BaseModel):
    report_type: Optional[str] = None
    filters: Optional[str] = None
    frequency: Optional[str] = None
    execution_time: Optional[str] = None
    recipients: Optional[str] = None
    format: Optional[str] = None
    is_active: Optional[bool] = None


class ScheduledReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    created_by: int
    report_type: str
    filters: Optional[str] = None
    frequency: str
    execution_time: str
    recipients: str
    format: str
    is_active: bool
    last_generated_at: Optional[datetime] = None
    last_status: Optional[str] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime