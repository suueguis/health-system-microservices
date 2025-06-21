from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import os

# Crear la aplicación FastAPI
app = FastAPI(
    title="Health System API Gateway", 
    description="Puerta principal del sistema de salud - conecta todos los microservicios",
    version="1.0.0"
)

# URLs de los microservicios - compatibles con Docker y desarrollo local
SERVICES = {
    "patients": os.getenv("PATIENTS_SERVICE_URL", "http://localhost:8081"),
    "doctors": os.getenv("DOCTORS_SERVICE_URL", "http://localhost:8082"), 
    "appointments": os.getenv("APPOINTMENTS_SERVICE_URL", "http://localhost:8083")
}

async def proxy_request(service_url: str, path: str, method: str, **kwargs) -> dict:
    """Función para reenviar peticiones a los microservicios"""
    url = f"{service_url}{path}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "PATCH":
                response = await client.patch(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                raise HTTPException(status_code=405, detail="Método no permitido")
            
            # Retornar la respuesta del microservicio
            return {
                "status_code": response.status_code,
                "content": response.json() if response.text else {},
                "headers": dict(response.headers)
            }
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Servicio no disponible: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/")
def root():
    """Endpoint principal del API Gateway"""
    return {
        "message": "Sistema de Salud API Gateway funcionando! 🏥",
        "description": "Sistema integral de gestión hospitalaria",
        "services": {
            "patients": f"{SERVICES['patients']} - Gestión de pacientes",
            "doctors": f"{SERVICES['doctors']} - Gestión de doctores", 
            "appointments": f"{SERVICES['appointments']} - Gestión de citas médicas"
        },
        "version": "1.0.0",
        "endpoints": {
            "patients": "/api/patients",
            "doctors": "/api/doctors",
            "appointments": "/api/appointments",
            "dashboard": "/api/dashboard"
        }
    }

@app.get("/health")
async def health_check():
    """Verificar la salud de todos los servicios"""
    health_status = {"gateway": "healthy", "services": {}}
    
    for service_name, service_url in SERVICES.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                if response.status_code == 200:
                    health_status["services"][service_name] = "healthy"
                else:
                    health_status["services"][service_name] = "unhealthy"
        except:
            health_status["services"][service_name] = "unreachable"
    
    return health_status

# ==================== PATIENTS ROUTES ====================

@app.get("/api/patients")
async def get_patients(request: Request):
    """Obtener todos los pacientes"""
    query_params = dict(request.query_params)
    result = await proxy_request(SERVICES["patients"], "/patients", "GET", params=query_params)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.post("/api/patients")
async def create_patient(request: Request):
    """Crear un paciente nuevo"""
    body = await request.json()
    result = await proxy_request(SERVICES["patients"], "/patients", "POST", json=body)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: int):
    """Obtener un paciente específico"""
    result = await proxy_request(SERVICES["patients"], f"/patients/{patient_id}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.put("/api/patients/{patient_id}")
async def update_patient(patient_id: int, request: Request):
    """Actualizar un paciente"""
    body = await request.json()
    result = await proxy_request(SERVICES["patients"], f"/patients/{patient_id}", "PUT", json=body)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.delete("/api/patients/{patient_id}")
async def delete_patient(patient_id: int):
    """Eliminar un paciente"""
    result = await proxy_request(SERVICES["patients"], f"/patients/{patient_id}", "DELETE")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/patients/search/{search_term}")
async def search_patients(search_term: str):
    """Buscar pacientes"""
    result = await proxy_request(SERVICES["patients"], f"/patients/search/{search_term}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/patients/document/{document_id}")
async def get_patient_by_document(document_id: str):
    """Obtener paciente por documento"""
    result = await proxy_request(SERVICES["patients"], f"/patients/document/{document_id}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

# ==================== DOCTORS ROUTES ====================

@app.get("/api/doctors")
async def get_doctors(request: Request):
    """Obtener todos los doctores"""
    query_params = dict(request.query_params)
    result = await proxy_request(SERVICES["doctors"], "/doctors", "GET", params=query_params)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.post("/api/doctors")
async def create_doctor(request: Request):
    """Crear un doctor nuevo"""
    body = await request.json()
    result = await proxy_request(SERVICES["doctors"], "/doctors", "POST", json=body)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/doctors/{doctor_id}")
async def get_doctor(doctor_id: int):
    """Obtener un doctor específico"""
    result = await proxy_request(SERVICES["doctors"], f"/doctors/{doctor_id}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.put("/api/doctors/{doctor_id}")
async def update_doctor(doctor_id: int, request: Request):
    """Actualizar un doctor"""
    body = await request.json()
    result = await proxy_request(SERVICES["doctors"], f"/doctors/{doctor_id}", "PUT", json=body)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.delete("/api/doctors/{doctor_id}")
async def delete_doctor(doctor_id: int):
    """Eliminar un doctor"""
    result = await proxy_request(SERVICES["doctors"], f"/doctors/{doctor_id}", "DELETE")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/doctors/search/{search_term}")
async def search_doctors(search_term: str):
    """Buscar doctores"""
    result = await proxy_request(SERVICES["doctors"], f"/doctors/search/{search_term}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/doctors/specialty/{specialty}")
async def get_doctors_by_specialty(specialty: str):
    """Obtener doctores por especialidad"""
    result = await proxy_request(SERVICES["doctors"], f"/doctors/specialty/{specialty}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/doctors/license/{license_number}")
async def get_doctor_by_license(license_number: str):
    """Obtener doctor por licencia"""
    result = await proxy_request(SERVICES["doctors"], f"/doctors/license/{license_number}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

# ==================== APPOINTMENTS ROUTES ====================

@app.get("/api/appointments")
async def get_appointments(request: Request):
    """Obtener todas las citas"""
    query_params = dict(request.query_params)
    result = await proxy_request(SERVICES["appointments"], "/appointments", "GET", params=query_params)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.post("/api/appointments")
async def create_appointment(request: Request):
    """Crear una cita nueva"""
    body = await request.json()
    result = await proxy_request(SERVICES["appointments"], "/appointments", "POST", json=body)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/appointments/{appointment_id}")
async def get_appointment(appointment_id: int):
    """Obtener una cita específica"""
    result = await proxy_request(SERVICES["appointments"], f"/appointments/{appointment_id}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.put("/api/appointments/{appointment_id}")
async def update_appointment(appointment_id: int, request: Request):
    """Actualizar una cita"""
    body = await request.json()
    result = await proxy_request(SERVICES["appointments"], f"/appointments/{appointment_id}", "PUT", json=body)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.delete("/api/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: int):
    """Cancelar una cita"""
    result = await proxy_request(SERVICES["appointments"], f"/appointments/{appointment_id}", "DELETE")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/appointments/patient/{patient_id}")
async def get_patient_appointments(patient_id: int):
    """Obtener citas de un paciente"""
    result = await proxy_request(SERVICES["appointments"], f"/appointments/patient/{patient_id}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.get("/api/appointments/doctor/{doctor_id}")
async def get_doctor_appointments(doctor_id: int):
    """Obtener citas de un doctor"""
    result = await proxy_request(SERVICES["appointments"], f"/appointments/doctor/{doctor_id}", "GET")
    return JSONResponse(content=result["content"], status_code=result["status_code"])

@app.patch("/api/appointments/{appointment_id}/complete")
async def complete_appointment(appointment_id: int, request: Request):
    """Completar una cita con diagnóstico"""
    body = await request.json()
    result = await proxy_request(SERVICES["appointments"], f"/appointments/{appointment_id}/complete", "PATCH", json=body)
    return JSONResponse(content=result["content"], status_code=result["status_code"])

# ==================== DASHBOARD Y REPORTES ====================

@app.get("/api/dashboard")
async def dashboard():
    """Dashboard con estadísticas del sistema de salud"""
    dashboard_data = {"title": "Dashboard Sistema de Salud", "timestamp": "2025-06-20"}
    
    try:
        # Obtener estadísticas de pacientes
        patients_result = await proxy_request(SERVICES["patients"], "/patients", "GET", params={"limit": 1000})
        if patients_result["status_code"] == 200:
            patients = patients_result["content"]
            dashboard_data["patients"] = {
                "total": len(patients),
                "active": len([p for p in patients if p.get("is_active", False)]),
                "by_gender": {
                    "masculino": len([p for p in patients if p.get("gender") == "masculino"]),
                    "femenino": len([p for p in patients if p.get("gender") == "femenino"])
                }
            }
        
        # Obtener estadísticas de doctores
        doctors_result = await proxy_request(SERVICES["doctors"], "/doctors", "GET", params={"limit": 1000})
        if doctors_result["status_code"] == 200:
            doctors = doctors_result["content"]
            dashboard_data["doctors"] = {
                "total": len(doctors),
                "available": len([d for d in doctors if d.get("is_available", False)]),
                "by_specialty": {}
            }
            # Contar por especialidad
            for doctor in doctors:
                specialty = doctor.get("specialty", "unknown")
                dashboard_data["doctors"]["by_specialty"][specialty] = dashboard_data["doctors"]["by_specialty"].get(specialty, 0) + 1
        
        # Obtener estadísticas de citas
        appointments_result = await proxy_request(SERVICES["appointments"], "/appointments", "GET", params={"limit": 1000})
        if appointments_result["status_code"] == 200:
            appointments = appointments_result["content"]
            dashboard_data["appointments"] = {
                "total": len(appointments),
                "today": 0,  # Se podría calcular con fecha actual
                "by_status": {}
            }
            # Contar por estado
            for appointment in appointments:
                status = appointment.get("status", "unknown")
                dashboard_data["appointments"]["by_status"][status] = dashboard_data["appointments"]["by_status"].get(status, 0) + 1
        
    except Exception as e:
        dashboard_data["error"] = f"Error obteniendo datos del dashboard: {str(e)}"
    
    return dashboard_data

@app.get("/api/reports/monthly")
async def monthly_report():
    """Reporte mensual del sistema"""
    return {
        "message": "Reporte mensual generado",
        "period": "Junio 2025",
        "note": "Funcionalidad disponible - implementación completa requiere análisis de fechas"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)