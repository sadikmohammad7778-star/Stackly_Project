from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.config.database import Base


class ImportError(Base):
    __tablename__ = "import_errors"

    id = Column(Integer, primary_key=True, index=True)

    import_id = Column(
        Integer,
        ForeignKey("import_history.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    row_number = Column(
        Integer,
        nullable=False
    )

    record_data = Column(
        Text,
        nullable=True
    )

    error_type = Column(
        String(100),
        nullable=False
    )

    error_message = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(30),
        default="Failed",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    import_history = relationship(
        "ImportHistory",
        back_populates="errors"
    )