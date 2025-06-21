from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./appointments.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AppointmentDB(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, nullable=False, index=True)
    doctor_id = Column(Integer, nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)
    appointment_type = Column(String(50), nullable=False)
    priority = Column(String(20), default="normal")
    status = Column(String(20), default="programada")
    reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    total_cost = Column(Float, nullable=False, default=0.0)
    diagnosis = Column(Text, nullable=True)
    treatment = Column(Text, nullable=True)
    next_appointment_needed = Column(Boolean, default=False)
    next_appointment_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()