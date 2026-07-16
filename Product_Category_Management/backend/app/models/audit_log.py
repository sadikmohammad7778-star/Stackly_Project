from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.config.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    entity_name = Column(String(150), nullable=False)
    action = Column(String(100), nullable=False)
    performed_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())