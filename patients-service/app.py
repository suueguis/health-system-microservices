from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, PatientDB
from models import Patient, PatientCreate, PatientUpdate
from datetime import datetime, date

app = FastAPI(
    title="Patients Service", 
    description="Servicio para manejar pacientes del sistema de salud",
    version="1.0.0"
)

def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@app.get("/")
def root():
    return {"message": "Patients Service funcionando correctamente! 🏥"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "patients"}

@app.post("/patients", response_model=Patient)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe un paciente con el mismo documento
    existing_patient = db.query(PatientDB).filter(PatientDB.document_id == patient.document_id).first()
    if existing_patient:
        raise HTTPException(status_code=400, detail="Ya existe un paciente con ese número de documento")
    
    # Verificar si ya existe un paciente con el mismo email
    existing_email = db.query(PatientDB).filter(PatientDB.email == patient.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Ya existe un paciente con ese email")
    
    # Verificar que la fecha de nacimiento sea válida
    if patient.birth_date >= date.today():
        raise HTTPException(status_code=400, detail="La fecha de nacimiento debe ser anterior a hoy")
    
    # Crear el paciente en la base de datos
    db_patient = PatientDB(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    # Agregar la edad calculada antes de retornar
    patient_dict = db_patient.__dict__.copy()
    patient_dict['age'] = calculate_age(db_patient.birth_date)
    
    return patient_dict

@app.get("/patients", response_model=List[Patient])
def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    active_only: bool = Query(True),
    blood_type: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(PatientDB)
    
    if active_only:
        query = query.filter(PatientDB.is_active == True)
    if blood_type:
        query = query.filter(PatientDB.blood_type == blood_type)
    if gender:
        query = query.filter(PatientDB.gender == gender)
    
    patients = query.offset(skip).limit(limit).all()
    
    patients_with_age = []
    for patient in patients:
        patient_dict = patient.__dict__.copy()
        patient_dict['age'] = calculate_age(patient.birth_date)
        patients_with_age.append(patient_dict)
    
    return patients_with_age

@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    patient_dict = patient.__dict__.copy()
    patient_dict['age'] = calculate_age(patient.birth_date)
    
    return patient_dict

@app.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient_update: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    update_data = patient_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db_patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_patient)
    
    patient_dict = db_patient.__dict__.copy()
    patient_dict['age'] = calculate_age(db_patient.birth_date)
    
    return patient_dict

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    db_patient.is_active = False
    db_patient.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Paciente {patient_id} desactivado correctamente"}

@app.get("/patients/search/{search_term}", response_model=List[Patient])
def search_patients(search_term: str, db: Session = Depends(get_db)):
    patients = db.query(PatientDB).filter(
        (PatientDB.full_name.ilike(f"%{search_term}%")) |
        (PatientDB.document_id.ilike(f"%{search_term}%")) |
        (PatientDB.email.ilike(f"%{search_term}%"))
    ).filter(PatientDB.is_active == True).all()
    
    patients_with_age = []
    for patient in patients:
        patient_dict = patient.__dict__.copy()
        patient_dict['age'] = calculate_age(patient.birth_date)
        patients_with_age.append(patient_dict)
    
    return patients_with_age

@app.get("/patients/document/{document_id}", response_model=Patient)
def get_patient_by_document(document_id: str, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.document_id == document_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    patient_dict = patient.__dict__.copy()
    patient_dict['age'] = calculate_age(patient.birth_date)
    
    return patient_dict

@app.patch("/patients/{patient_id}/activate")
def activate_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    db_patient.is_active = True
    db_patient.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Paciente {patient_id} activado correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)