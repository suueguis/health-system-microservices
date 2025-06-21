from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./doctors.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DoctorDB(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False, index=True)
    specialty = Column(String(50), nullable=False, index=True)
    license_number = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    phone = Column(String(15), nullable=False)
    office_address = Column(Text, nullable=False)
    working_days = Column(Text, nullable=False)  # JSON string
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    consultation_duration = Column(Integer, nullable=False)
    consultation_fee = Column(Float, nullable=False)
    years_experience = Column(Integer, nullable=False)
    biography = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()