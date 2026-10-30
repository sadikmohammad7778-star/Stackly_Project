from app.config.database import Base, engine

# Import models so SQLAlchemy registers their tables.
from app.models.permission import Permission
from app.models.role_permission import RolePermission

Base.metadata.create_all(
    bind=engine,
    tables=[
        Permission.__table__,
        RolePermission.__table__,
    ],
)

print("Data Governance tables created successfully.")