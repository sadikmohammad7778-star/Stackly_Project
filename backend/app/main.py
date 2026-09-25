import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

load_dotenv()

from app.config.database import engine, Base
from app.config.exceptions import global_exception_handler

from app.models.company import Company
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import Attendance
from app.models.category import Category
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.notification import Notification
from app.models.demand_forecast import DemandForecast
from app.models.forecast_history import ForecastHistory
from app.models.import_history import ImportHistory
from app.models.import_error import ImportError
from app.models.report_history import ReportHistory
from app.models.scheduled_report import ScheduledReport
from app.models.data_quality import DataQualityIssue, ReconciliationRun


from app.routes.company_routes import router as company_router
from app.routes.auth_routes import router as auth_router
from app.routes.employee_routes import router as employee_router
from app.routes.department_routes import router as department_router
from app.routes.attendance_routes import router as attendance_router
from app.routes.category_routes import router as category_router
from app.routes.product_routes import router as product_router
from app.routes.sale_routes import router as sale_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.report_routes import router as report_router
from app.routes.health_routes import router as health_router
from app.routes.inventory_routes import router as inventory_router
from app.routes.notification_routes import router as notification_router
from app.routes.export_routes import router as export_router
from app.routes.audit_routes import router as audit_router
from app.routes.customer_routes import router as customer_router
from app.routes.demand_forecast_routes import router as demand_forecast_router
from app.routes.inventory_forecasting_routes import router as inventory_forecasting_router
from app.routes.import_routes import router as import_router
from app.routes.scheduled_report_routes import router as scheduled_report_router

from app.services.report_scheduler_service import scheduled_report_worker

from app.routes.data_quality_routes import router as data_quality_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="RetailPulse Analytics API",
    version="1.0.0",
)


@app.on_event("startup")
async def start_report_scheduler():
    asyncio.create_task(scheduled_report_worker())


app.add_exception_handler(
    Exception,
    global_exception_handler,
)


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(company_router)
app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(attendance_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(sale_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(report_router)
app.include_router(health_router)
app.include_router(inventory_router)
app.include_router(notification_router)
app.include_router(export_router)
app.include_router(audit_router)
app.include_router(customer_router)
app.include_router(demand_forecast_router)
app.include_router(inventory_forecasting_router)
app.include_router(import_router)
app.include_router(scheduled_report_router)
app.include_router(data_quality_router)


@app.get("/routes")
def list_routes():
    routes = []

    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
            })

    return routes


@app.get("/")
def home():
    return {
        "message": "RetailPulse Analytics API is Running"
    }