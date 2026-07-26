from pydantic import BaseModel


# ----------------------------
# Existing Reports
# ----------------------------

class RevenueReport(BaseModel):
    today: float
    this_week: float
    this_month: float
    this_year: float


class InventoryReport(BaseModel):
    total_products: int
    in_stock: int
    low_stock: int
    out_of_stock: int
    inventory_value: float


# ----------------------------
# Dashboard KPIs
# ----------------------------

class DashboardKPIs(BaseModel):
    total_revenue: float
    total_orders: int
    total_products_sold: int
    average_order_value: float
    total_inventory_value: float
    low_stock_products: int
    out_of_stock_products: int
    total_categories: int


# ----------------------------
# Sales Analytics
# ----------------------------

class RevenueTrend(BaseModel):
    label: str
    revenue: float


class SalesTrend(BaseModel):
    label: str
    orders: int


class TopProduct(BaseModel):
    product_name: str
    quantity_sold: int


class TopCategory(BaseModel):
    category_name: str
    revenue: float


class PaymentMethodData(BaseModel):
    payment_method: str
    total: float


class SalesChannelData(BaseModel):
    sales_channel: str
    total: float


# ----------------------------
# Inventory Analytics
# ----------------------------

class InventoryDistribution(BaseModel):
    category: str
    quantity: int


class StockStatusSummary(BaseModel):
    status: str
    count: int


class InventoryValueByCategory(BaseModel):
    category: str
    value: float



class RevenueTrendItem(BaseModel):
    date: str
    revenue: float    

class TopProductItem(BaseModel):
    product_name: str
    quantity_sold: int    

class TopCategoryItem(BaseModel):
    category_name: str
    revenue: float    

class PaymentMethodItem(BaseModel):
    payment_method: str
    total_sales: float    

class SalesChannelItem(BaseModel):
    sales_channel: str
    total_sales: float

class InventoryCategoryItem(BaseModel):
    category_name: str
    stock: int    

class StockStatusItem(BaseModel):
    stock_status: str
    total_products: int    

class InventoryValueItem(BaseModel):
    category_name: str
    inventory_value: float    