from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config.settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)

from urllib.parse import quote_plus

encoded_password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{encoded_password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()