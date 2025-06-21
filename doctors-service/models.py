from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, time

class DoctorBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    specialty: str = Field(..., description="cardiologia, pediatria, dermatologia, etc.")
    license_number: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    office_address: str = Field(..., min_length=10, max_length=200)
    working_days: List[str] = Field(..., description="Lista de días: lunes, martes, etc.")
    start_time: time
    end_time: time
    consultation_duration: int = Field(..., gt=0, le=120)
    consultation_fee: float = Field(..., gt=0)
    years_experience: int = Field(..., ge=0, le=50)
    biography: Optional[str] = Field(None, max_length=1000)

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    specialty: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    office_address: Optional[str] = Field(None, min_length=10, max_length=200)
    working_days: Optional[List[str]] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    consultation_duration: Optional[int] = Field(None, gt=0, le=120)
    consultation_fee: Optional[float] = Field(None, gt=0)
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    biography: Optional[str] = Field(None, max_length=1000)

class Doctor(DoctorBase):
    id: int
    is_available: bool = True
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True