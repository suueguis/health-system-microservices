from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date

class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    document_id: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    birth_date: date
    gender: str = Field(..., description="masculino, femenino, otro")
    blood_type: Optional[str] = Field(None, description="A+, A-, B+, B-, AB+, AB-, O+, O-")
    address: str = Field(..., min_length=10, max_length=200)
    emergency_contact_name: str = Field(..., min_length=2, max_length=100)
    emergency_contact_phone: str = Field(..., min_length=10, max_length=15)
    medical_history: Optional[str] = Field(None, max_length=1000)
    allergies: Optional[str] = Field(None, max_length=500)
    current_medications: Optional[str] = Field(None, max_length=500)

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    blood_type: Optional[str] = None
    address: Optional[str] = Field(None, min_length=10, max_length=200)
    emergency_contact_name: Optional[str] = Field(None, min_length=2, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, min_length=10, max_length=15)
    medical_history: Optional[str] = Field(None, max_length=1000)
    allergies: Optional[str] = Field(None, max_length=500)
    current_medications: Optional[str] = Field(None, max_length=500)

class Patient(PatientBase):
    id: int
    age: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True