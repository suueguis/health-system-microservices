from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, AppointmentDB
from models import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentComplete
import httpx
from datetime import datetime, date, time, timedelta
import os

app = FastAPI(
    title="Appointments Service", 
    description="Servicio para manejar citas médicas del sistema de salud",
    version="1.0.0"
)

# URLs de otros servicios - compatibles con Docker y desarrollo local
PATIENTS_SERVICE_URL = os.getenv("PATIENTS_SERVICE_URL", "http://localhost:8081")
DOCTORS_SERVICE_URL = os.getenv("DOCTORS_SERVICE_URL", "http://localhost:8082")

async def verify_patient_exists(patient_id: int) -> Optional[dict]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PATIENTS_SERVICE_URL}/patients/{patient_id}")
            if response.status_code == 200:
                return response.json()
            return None
    except:
        return None

async def verify_doctor_exists(doctor_id: int) -> Optional[dict]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DOCTORS_SERVICE_URL}/doctors/{doctor_id}")
            if response.status_code == 200:
                return response.json()
            return None
    except:
        return None

def is_doctor_available(doctor_info: dict, appointment_date: date, appointment_time: time) -> bool:
    # Verificar día de la semana
    weekday_names = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    appointment_weekday = weekday_names[appointment_date.weekday()]
    
    if appointment_weekday not in doctor_info.get("working_days", []):
        return False
    
    # Verificar horario
    try:
        start_time = datetime.strptime(str(doctor_info["start_time"]), "%H:%M:%S").time()
        end_time = datetime.strptime(str(doctor_info["end_time"]), "%H:%M:%S").time()
        return start_time <= appointment_time <= end_time
    except:
        return True  # Si hay error, permitir

def has_scheduling_conflict(db: Session, doctor_id: int, appointment_date: date, appointment_time: time, 
                           duration: int, exclude_appointment_id: Optional[int] = None) -> bool:
    # Calcular tiempo de fin de la nueva cita
    start_datetime = datetime.combine(appointment_date, appointment_time)
    end_datetime = start_datetime + timedelta(minutes=duration)
    
    # Buscar citas existentes del doctor en la misma fecha
    query = db.query(AppointmentDB).filter(
        AppointmentDB.doctor_id == doctor_id,
        AppointmentDB.appointment_date == appointment_date,
        AppointmentDB.status.in_(["programada", "confirmada", "en_curso"])
    )
    
    if exclude_appointment_id:
        query = query.filter(AppointmentDB.id != exclude_appointment_id)
    
    existing_appointments = query.all()
    
    for existing in existing_appointments:
        existing_start = datetime.combine(appointment_date, existing.appointment_time)
        existing_end = existing_start + timedelta(minutes=30)  # Asumimos 30 min por defecto
        
        # Verificar solapamiento
        if (start_datetime < existing_end) and (end_datetime > existing_start):
            return True
    
    return False

@app.get("/")
def root():
    return {"message": "Appointments Service funcionando correctamente! 📅"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "appointments"}

@app.post("/appointments", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Verificar que el paciente existe
    patient_info = await verify_patient_exists(appointment.patient_id)
    if not patient_info:
        raise HTTPException(status_code=400, detail="Paciente no encontrado")
    
    # Verificar que el doctor existe
    doctor_info = await verify_doctor_exists(appointment.doctor_id)
    if not doctor_info:
        raise HTTPException(status_code=400, detail="Doctor no encontrado")
    
    # Verificar que la fecha no sea en el pasado
    if appointment.appointment_date < date.today():
        raise HTTPException(status_code=400, detail="No se pueden programar citas en fechas pasadas")
    
    # Verificar disponibilidad del doctor
    if not is_doctor_available(doctor_info, appointment.appointment_date, appointment.appointment_time):
        raise HTTPException(
            status_code=400, 
            detail="El doctor no está disponible en ese día y horario"
        )
    
    # Verificar conflictos de horario
    consultation_duration = doctor_info.get("consultation_duration", 30)
    if has_scheduling_conflict(db, appointment.doctor_id, appointment.appointment_date, 
                             appointment.appointment_time, consultation_duration):
        raise HTTPException(
            status_code=400, 
            detail="El doctor ya tiene una cita programada en ese horario"
        )
    
    # Crear la cita en la base de datos
    db_appointment = AppointmentDB(
        **appointment.dict(),
        total_cost=doctor_info["consultation_fee"],
        status="programada"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Agregar información del paciente y doctor para la respuesta
    appointment_dict = db_appointment.__dict__.copy()
    appointment_dict['patient_name'] = patient_info['full_name']
    appointment_dict['doctor_name'] = doctor_info['full_name']
    appointment_dict['doctor_specialty'] = doctor_info['specialty']
    
    return appointment_dict

@app.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    appointment_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(AppointmentDB)
    
    if patient_id:
        query = query.filter(AppointmentDB.patient_id == patient_id)
    if doctor_id:
        query = query.filter(AppointmentDB.doctor_id == doctor_id)
    if status:
        query = query.filter(AppointmentDB.status == status)
    if appointment_date:
        query = query.filter(AppointmentDB.appointment_date == appointment_date)
    
    appointments = query.offset(skip).limit(limit).all()
    
    # Enriquecer con información de pacientes y doctores
    enriched_appointments = []
    for appointment in appointments:
        appointment_dict = appointment.__dict__.copy()
        
        # Obtener información del paciente y doctor
        patient_info = await verify_patient_exists(appointment.patient_id)
        doctor_info = await verify_doctor_exists(appointment.doctor_id)
        
        if patient_info:
            appointment_dict['patient_name'] = patient_info['full_name']
        if doctor_info:
            appointment_dict['doctor_name'] = doctor_info['full_name']
            appointment_dict['doctor_specialty'] = doctor_info['specialty']
        
        enriched_appointments.append(appointment_dict)
    
    return enriched_appointments

@app.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # Enriquecer con información de paciente y doctor
    appointment_dict = appointment.__dict__.copy()
    
    patient_info = await verify_patient_exists(appointment.patient_id)
    doctor_info = await verify_doctor_exists(appointment.doctor_id)
    
    if patient_info:
        appointment_dict['patient_name'] = patient_info['full_name']
    if doctor_info:
        appointment_dict['doctor_name'] = doctor_info['full_name']
        appointment_dict['doctor_specialty'] = doctor_info['specialty']
    
    return appointment_dict

@app.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: int, appointment_update: AppointmentUpdate, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    # No permitir actualizar citas completadas o canceladas
    if db_appointment.status in ["completada", "cancelada"]:
        raise HTTPException(status_code=400, detail="No se puede modificar una cita completada o cancelada")
    
    # Actualizar solo los campos que se enviaron
    update_data = appointment_update.dict(exclude_unset=True)
    
    # Si se cambia fecha u hora, verificar disponibilidad
    if 'appointment_date' in update_data or 'appointment_time' in update_data:
        new_date = update_data.get('appointment_date', db_appointment.appointment_date)
        new_time = update_data.get('appointment_time', db_appointment.appointment_time)
        
        # Verificar disponibilidad del doctor
        doctor_info = await verify_doctor_exists(db_appointment.doctor_id)
        if doctor_info and not is_doctor_available(doctor_info, new_date, new_time):
            raise HTTPException(status_code=400, detail="El doctor no está disponible en ese nuevo horario")
        
        # Verificar conflictos
        consultation_duration = doctor_info.get("consultation_duration", 30) if doctor_info else 30
        if has_scheduling_conflict(db, db_appointment.doctor_id, new_date, new_time, 
                                 consultation_duration, appointment_id):
            raise HTTPException(status_code=400, detail="Conflicto de horario con otra cita")
    
    for field, value in update_data.items():
        setattr(db_appointment, field, value)
    
    db_appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_appointment)
    
    # Enriquecer respuesta
    appointment_dict = db_appointment.__dict__.copy()
    patient_info = await verify_patient_exists(db_appointment.patient_id)
    doctor_info = await verify_doctor_exists(db_appointment.doctor_id)
    
    if patient_info:
        appointment_dict['patient_name'] = patient_info['full_name']
    if doctor_info:
        appointment_dict['doctor_name'] = doctor_info['full_name']
        appointment_dict['doctor_specialty'] = doctor_info['specialty']
    
    return appointment_dict

@app.delete("/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    if db_appointment.status in ["completada", "cancelada"]:
        raise HTTPException(status_code=400, detail="No se puede cancelar una cita completada o ya cancelada")
    
    db_appointment.status = "cancelada"
    db_appointment.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Cita {appointment_id} cancelada correctamente"}

@app.patch("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int, completion_data: AppointmentComplete, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    if db_appointment.status == "completada":
        raise HTTPException(status_code=400, detail="La cita ya está completada")
    
    if db_appointment.status == "cancelada":
        raise HTTPException(status_code=400, detail="No se puede completar una cita cancelada")
    
    # Actualizar con la información de completación
    db_appointment.status = "completada"
    db_appointment.diagnosis = completion_data.diagnosis
    db_appointment.treatment = completion_data.treatment
    db_appointment.next_appointment_needed = completion_data.next_appointment_needed
    db_appointment.next_appointment_notes = completion_data.next_appointment_notes
    db_appointment.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": f"Cita {appointment_id} completada correctamente"}

@app.get("/appointments/patient/{patient_id}", response_model=List[Appointment])
async def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    # Verificar que el paciente existe
    patient_info = await verify_patient_exists(patient_id)
    if not patient_info:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    appointments = db.query(AppointmentDB).filter(AppointmentDB.patient_id == patient_id).all()
    
    # Enriquecer con información del doctor
    enriched_appointments = []
    for appointment in appointments:
        appointment_dict = appointment.__dict__.copy()
        appointment_dict['patient_name'] = patient_info['full_name']
        
        doctor_info = await verify_doctor_exists(appointment.doctor_id)
        if doctor_info:
            appointment_dict['doctor_name'] = doctor_info['full_name']
            appointment_dict['doctor_specialty'] = doctor_info['specialty']
        
        enriched_appointments.append(appointment_dict)
    
    return enriched_appointments

@app.get("/appointments/doctor/{doctor_id}", response_model=List[Appointment])
async def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):
    # Verificar que el doctor existe
    doctor_info = await verify_doctor_exists(doctor_id)
    if not doctor_info:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    appointments = db.query(AppointmentDB).filter(AppointmentDB.doctor_id == doctor_id).all()
    
    # Enriquecer con información del paciente
    enriched_appointments = []
    for appointment in appointments:
        appointment_dict = appointment.__dict__.copy()
        appointment_dict['doctor_name'] = doctor_info['full_name']
        appointment_dict['doctor_specialty'] = doctor_info['specialty']
        
        patient_info = await verify_patient_exists(appointment.patient_id)
        if patient_info:
            appointment_dict['patient_name'] = patient_info['full_name']
        
        enriched_appointments.append(appointment_dict)
    
    return enriched_appointments

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)