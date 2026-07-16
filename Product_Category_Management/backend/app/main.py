from fastapi import FastAPI

from app.config.database import Base, engine

from app.models.category import Category
from app.models.product import Product
from app.models.audit_log import AuditLog
from fastapi.middleware.cors import CORSMiddleware


from app.routes.category_routes import router as category_router
from app.routes.product_routes import router as product_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.audit_routes import router as audit_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Management API",
    version="1.0"
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

app.include_router(category_router)
app.include_router(product_router)
app.include_router(dashboard_router)
app.include_router(audit_router)

@app.get("/")
def home():
    return {
        "message": "Product & Category Management API Running Successfully"
    }