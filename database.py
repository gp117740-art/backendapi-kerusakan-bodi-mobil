from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL Koneksi PostgreSQL (User: galihputra, Database: db_project_deteksi_body_mobil)
DATABASE_URL = "postgresql://galihputra:sqlkeren@localhost:5432/db_project_deteksi_body_mobil"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fungsi get_db yang dibutuhkan oleh main.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 