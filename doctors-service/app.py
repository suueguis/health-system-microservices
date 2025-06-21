from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, DoctorDB
from models import Doctor, DoctorCreate, DoctorUpdate
from datetime import datetime
import json

app = FastAPI(
    title="Doctors Service", 
    description="Servicio para manejar doctores del sistema de salud",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Doctors Service funcionando correctamente! 👨‍⚕️"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "doctors"}

@app.post("/doctors", response_model=Doctor)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe un doctor con el mismo número de licencia
    existing_doctor = db.query(DoctorDB).filter(DoctorDB.license_number == doctor.license_number).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Ya existe un doctor con ese número de licencia")
    
    # Verificar si ya existe un doctor con el mismo email
    existing_email = db.query(DoctorDB).filter(DoctorDB.email == doctor.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Ya existe un doctor con ese email")
    
    # Validar horarios
    if doctor.start_time >= doctor.end_time:
        raise HTTPException(status_code=400, detail="La hora de inicio debe ser anterior a la hora de fin")
    
    # Crear el doctor en la base de datos
    doctor_data = doctor.dict()
    # Convertir working_days a JSON string
    doctor_data['working_days'] = json.dumps(doctor.working_days)
    
    db_doctor = DoctorDB(**doctor_data)
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    
    # Convertir de vuelta para la respuesta
    doctor_dict = db_doctor.__dict__.copy()
    doctor_dict['working_days'] = json.loads(db_doctor.working_days)
    
    return doctor_dict

@app.get("/doctors", response_model=List[Doctor])
def get_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    specialty: Optional[str] = Query(None),
    available_only: bool = Query(True),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    query = db.query(DoctorDB)
    
    if active_only:
        query = query.filter(DoctorDB.is_active == True)
    if available_only:
        query = query.filter(DoctorDB.is_available == True)
    if specialty:
        query = query.filter(DoctorDB.specialty.ilike(f"%{specialty}%"))
    
    doctors = query.offset(skip).limit(limit).all()
    
    doctors_with_days = []
    for doctor in doctors:
        doctor_dict = doctor.__dict__.copy()
        doctor_dict['working_days'] = json.loads(doctor.working_days)
        doctors_with_days.append(doctor_dict)
    
    return doctors_with_days

@app.get("/doctors/{doctor_id}", response_model=Doctor)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    doctor_dict = doctor.__dict__.copy()
    doctor_dict['working_days'] = json.loads(doctor.working_days)
    
    return doctor_dict

@app.put("/doctors/{doctor_id}", response_model=Doctor)
def update_doctor(doctor_id: int, doctor_update: DoctorUpdate, db: Session = Depends(get_db)):
    db_doctor = db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    update_data = doctor_update.dict(exclude_unset=True)
    
    if 'working_days' in update_data:
        update_data['working_days'] = json.dumps(update_data['working_days'])
    
    if 'start_time' in update_data and 'end_time' in update_data:
        if update_data['start_time'] >= update_data['end_time']:
            raise HTTPException(status_code=400, detail="La hora de inicio debe ser anterior a la hora de fin")
    
    for field, value in update_data.items():
        setattr(db_doctor, field, value)
    
    db_doctor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_doctor)
    
    doctor_dict = db_doctor.__dict__.copy()
    doctor_dict['working_days'] = json.loads(db_doctor.working_days)
    
    return doctor_dict

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    db_doctor.is_active = False
    db_doctor.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Doctor {doctor_id} desactivado correctamente"}

@app.get("/doctors/search/{search_term}", response_model=List[Doctor])
def search_doctors(search_term: str, db: Session = Depends(get_db)):
    doctors = db.query(DoctorDB).filter(
        (DoctorDB.full_name.ilike(f"%{search_term}%")) |
        (DoctorDB.specialty.ilike(f"%{search_term}%")) |
        (DoctorDB.license_number.ilike(f"%{search_term}%"))
    ).filter(DoctorDB.is_active == True).all()
    
    doctors_with_days = []
    for doctor in doctors:
        doctor_dict = doctor.__dict__.copy()
        doctor_dict['working_days'] = json.loads(doctor.working_days)
        doctors_with_days.append(doctor_dict)
    
    return doctors_with_days

@app.get("/doctors/specialty/{specialty}", response_model=List[Doctor])
def get_doctors_by_specialty(specialty: str, db: Session = Depends(get_db)):
    doctors = db.query(DoctorDB).filter(
        DoctorDB.specialty.ilike(f"%{specialty}%"),
        DoctorDB.is_active == True,
        DoctorDB.is_available == True
    ).all()
    
    doctors_with_days = []
    for doctor in doctors:
        doctor_dict = doctor.__dict__.copy()
        doctor_dict['working_days'] = json.loads(doctor.working_days)
        doctors_with_days.append(doctor_dict)
    
    return doctors_with_days

@app.patch("/doctors/{doctor_id}/availability")
def toggle_availability(doctor_id: int, available: bool, db: Session = Depends(get_db)):
    db_doctor = db.query(DoctorDB).filter(DoctorDB.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    db_doctor.is_available = available
    db_doctor.updated_at = datetime.utcnow()
    db.commit()
    
    status = "disponible" if available else "no disponible"
    return {"message": f"Doctor {doctor_id} marcado como {status}"}

@app.get("/doctors/license/{license_number}", response_model=Doctor)
def get_doctor_by_license(license_number: str, db: Session = Depends(get_db)):
    doctor = db.query(DoctorDB).filter(DoctorDB.license_number == license_number).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    doctor_dict = doctor.__dict__.copy()
    doctor_dict['working_days'] = json.loads(doctor.working_days)
    
    return doctor_dict

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)