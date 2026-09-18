from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.config.database import Base


class ImportError(Base):
    __tablename__ = "import_errors"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    import_id = Column(
        Integer,
        ForeignKey(
            "import_history.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    row_number = Column(
        Integer,
        nullable=False,
    )

    error_type = Column(
        String(50),
        nullable=False,
    )

    error_message = Column(
        Text,
        nullable=False,
    )

    import_history = relationship(
        "ImportHistory",
        back_populates="errors",
    )