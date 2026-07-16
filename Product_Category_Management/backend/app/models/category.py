from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.config.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)

    name = Column(String(100), nullable=False)
    description = Column(String(255))
    status = Column(String(20), default="Active")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())