"""
Лабораторна робота №2 - підключення до PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Параметри підключення до PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dental_db"
DB_USER = "postgres"
DB_PASSWORD = "password"  # замінити на реальний пароль

DATABASE_URL = f"postgresql+psycopg2://postgres:123456@localhost:5433/dental_db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
