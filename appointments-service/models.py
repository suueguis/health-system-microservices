from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time

class AppointmentBase(BaseModel):
    patient_id: int = Field(..., description="ID del paciente")
    doctor_id: int = Field(..., description="ID del doctor")
    appointment_date: date = Field(..., description="Fecha de la cita")
    appointment_time: time = Field(..., description="Hora de la cita")
    appointment_type: str = Field(..., description="consulta, control, emergencia, etc.")
    priority: str = Field("normal", description="baja, normal, alta, urgente")
    reason: str = Field(..., min_length=10, max_length=500, description="Motivo de la consulta")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    appointment_type: Optional[str] = None
    priority: Optional[str] = None
    reason: Optional[str] = Field(None, min_length=10, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = None

class AppointmentComplete(BaseModel):
    diagnosis: str = Field(..., min_length=10, max_length=1000, description="Diagnóstico médico")
    treatment: Optional[str] = Field(None, max_length=1000, description="Tratamiento prescrito")
    next_appointment_needed: bool = Field(False, description="¿Necesita próxima cita?")
    next_appointment_notes: Optional[str] = Field(None, max_length=500, description="Notas para próxima cita")

class Appointment(AppointmentBase):
    id: int
    status: str
    total_cost: float
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    next_appointment_needed: bool = False
    next_appointment_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Información adicional del paciente y doctor
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_specialty: Optional[str] = None
    
    class Config:
        from_attributes = True