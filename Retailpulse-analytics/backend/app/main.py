from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.config.database import engine, Base


# Import models
from app.models.company import Company
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import Attendance



# Import routes
from app.routes.company_routes import router as company_router
from app.routes.auth_routes import router as auth_router
from app.routes.employee_routes import router as employee_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.department_routes import router as department_router

# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="RetailPulse Analytics API",
    version="1.0.0"
)
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.config.exceptions import register_exception_handlers
register_exception_handlers(app)

app.include_router(company_router)
app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(department_router)


@app.get("/")
def home():
    return {
        "message": "RetailPulse Analytics API is Running"
    }