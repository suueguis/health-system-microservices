# 🏥 Sistema de Salud - Microservicios

**Autora:** Susana Eguis Muñoz  
**Proyecto:** Sistema distribuido de gestión hospitalaria con arquitectura de microservicios  
**Tecnologías:** Python, FastAPI, SQLite, Docker  

## 📋 Descripción

Sistema integral de gestión hospitalaria implementado con arquitectura de microservicios. Permite gestionar pacientes, doctores y citas médicas de manera distribuida, escalable y mantenible.

### ✨ Características Principales

- **🏥 Gestión de Pacientes**: Registro completo con historial médico, alergias y medicamentos
- **👨‍⚕️ Gestión de Doctores**: Especialidades, horarios, tarifas y disponibilidad
- **📅 Gestión de Citas**: Sistema inteligente que evita conflictos de horarios
- **🚪 API Gateway**: Punto de entrada único con enrutamiento automático
- **🐳 Docker**: Containerización completa para fácil despliegue
- **📊 Dashboard**: Estadísticas en tiempo real del sistema
- **🧪 Pruebas**: Colección completa de Postman incluida

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Patients      │    │    Doctors      │    │  Appointments   │
│   Service       │    │   Service       │    │    Service      │
│   (Puerto 8081) │    │  (Puerto 8082)  │    │  (Puerto 8083)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Gateway   │
                    │  (Puerto 8080)  │
                    └─────────────────┘
```

### 🎯 Microservicios

1. **Patients Service (8081)**: Gestión completa de pacientes
2. **Doctors Service (8082)**: Gestión de médicos y especialidades  
3. **Appointments Service (8083)**: Sistema de citas con validaciones
4. **API Gateway (8080)**: Enrutamiento y punto de entrada único

## 📁 Estructura del Proyecto

```
health-system-microservices/
├── 📄 docker-compose.yml           # Configuración Docker
├── 📄 README.md                    # Este archivo
├── 🏥 patients-service/            # Servicio de Pacientes
│   ├── app.py                      # API del servicio
│   ├── models.py                   # Modelos de datos
│   ├── database.py                 # Configuración BD
│   ├── requirements.txt            # Dependencias
│   └── Dockerfile                  # Imagen Docker
├── 👨‍⚕️ doctors-service/             # Servicio de Doctores
│   ├── app.py
│   ├── models.py
│   ├── database.py
│   ├── requirements.txt
│   └── Dockerfile
├── 📅 appointments-service/        # Servicio de Citas
│   ├── app.py
│   ├── models.py
│   ├── database.py
│   ├── requirements.txt
│   └── Dockerfile
├── 🚪 api-gateway/                 # Gateway Principal
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── 🧪 postman/                     # Pruebas
    └── Health-System-Tests.postman_collection.json
```

## 🚀 Guía de Instalación y Uso

### Prerrequisitos

- **Python 3.11+** instalado
- **Docker Desktop** instalado (opcional pero recomendado)
- **Git** para clonar el repositorio
- **Postman** para ejecutar pruebas (opcional)

### 📥 Paso 1: Clonar el Repositorio

```bash
git clone [URL-DEL-REPOSITORIO]
cd health-system-microservices
```

### 🐳 Opción A: Ejecutar con Docker (Recomendado)

**1. Iniciar Docker Desktop**

**2. Construir y ejecutar todos los servicios:**
```bash
docker-compose up --build
```

**3. Verificar que funciona:**
- Ve a: http://localhost:8080
- Deberías ver información del API Gateway

**4. Para detener:**
```bash
docker-compose down
```

### 🐍 Opción B: Ejecutar Manualmente

**1. Instalar dependencias en cada servicio:**

```bash
# Patients Service
cd patients-service
pip install -r requirements.txt
python app.py
# Dejar corriendo y abrir nueva terminal

# Doctors Service  
cd doctors-service
pip install -r requirements.txt
python app.py
# Dejar corriendo y abrir nueva terminal

# Appointments Service
cd appointments-service
pip install -r requirements.txt
python app.py
# Dejar corriendo y abrir nueva terminal

# API Gateway
cd api-gateway
pip install -r requirements.txt
python app.py
```

**2. Verificar servicios:**
- Patients: http://localhost:8081
- Doctors: http://localhost:8082  
- Appointments: http://localhost:8083
- Gateway: http://localhost:8080

## 🧪 Ejecutar Pruebas

### Con Postman

**1. Importar colección:**
- Abrir Postman
- File → Import
- Seleccionar: `postman/Health-System-Tests.postman_collection.json`

**2. Ejecutar pruebas en orden:**
1. **Health Checks** - Verificar servicios
2. **Create Patient - Juan Pérez**
3. **Create Patient - María González**  
4. **Create Doctor - Dr. García**
5. **Create Doctor - Dra. Martínez**
6. **Create Appointment - Juan con Dr. García**
7. **Get Dashboard Data**

### Pruebas Manuales con cURL

```bash
# Verificar health
curl http://localhost:8080/health

# Crear paciente
curl -X POST http://localhost:8080/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Juan Pérez",
    "document_id": "12345678",
    "email": "juan@test.com",
    "phone": "3001234567",
    "birth_date": "1990-01-01",
    "gender": "masculino",
    "address": "Bogotá, Colombia",
    "emergency_contact_name": "María",
    "emergency_contact_phone": "3009876543"
  }'

# Ver pacientes
curl http://localhost:8080/api/patients
```

## 📊 Endpoints Principales

### 🏥 Pacientes
```
GET    /api/patients              # Listar pacientes
POST   /api/patients              # Crear paciente
GET    /api/patients/{id}         # Ver paciente
PUT    /api/patients/{id}         # Actualizar paciente
DELETE /api/patients/{id}         # Desactivar paciente
GET    /api/patients/search/{term} # Buscar pacientes
```

### 👨‍⚕️ Doctores
```
GET    /api/doctors               # Listar doctores
POST   /api/doctors               # Crear doctor
GET    /api/doctors/{id}          # Ver doctor
PUT    /api/doctors/{id}          # Actualizar doctor
DELETE /api/doctors/{id}          # Desactivar doctor
GET    /api/doctors/specialty/{spec} # Por especialidad
```

### 📅 Citas
```
GET    /api/appointments          # Listar citas
POST   /api/appointments          # Crear cita
GET    /api/appointments/{id}     # Ver cita
PUT    /api/appointments/{id}     # Actualizar cita
DELETE /api/appointments/{id}     # Cancelar cita
PATCH  /api/appointments/{id}/complete # Completar cita
```

### 📊 Dashboard
```
GET    /api/dashboard             # Estadísticas generales
GET    /health                    # Estado de servicios
```

## 📖 Documentación API

**FastAPI genera documentación automática:**

- **Gateway**: http://localhost:8080/docs
- **Patients**: http://localhost:8081/docs  
- **Doctors**: http://localhost:8082/docs
- **Appointments**: http://localhost:8083/docs

## 🔧 Configuración

### Variables de Entorno

Para Docker, los servicios se comunican automáticamente. Para desarrollo local, puedes configurar:

```bash
# En appointments-service y api-gateway
export PATIENTS_SERVICE_URL=http://localhost:8081
export DOCTORS_SERVICE_URL=http://localhost:8082
export APPOINTMENTS_SERVICE_URL=http://localhost:8083
```

### Bases de Datos

Cada servicio usa SQLite:
- `patients-service/patients.db`
- `doctors-service/doctors.db`
- `appointments-service/appointments.db`

## 🐛 Solución de Problemas

### Docker no funciona
```bash
# Limpiar Docker
docker-compose down -v
docker system prune -f
docker-compose up --build
```

### Error de puertos ocupados
```bash
# Ver qué usa el puerto
netstat -an | findstr :8080

# Cambiar puertos en docker-compose.yml si es necesario
```

### Servicios no se comunican
- Verificar que todos los servicios estén corriendo
- Revisar logs: `docker-compose logs [service-name]`
- Verificar URLs en variables de entorno

## 🎯 Casos de Uso Implementados

1. **Registro de Pacientes**: Con historial médico completo
2. **Gestión de Doctores**: Especialidades y horarios  
3. **Programación de Citas**: Con validación de disponibilidad
4. **Prevención de Conflictos**: No permite citas solapadas
5. **Comunicación Inter-servicios**: Validación automática
6. **Dashboard Estadístico**: Métricas en tiempo real

## 🏆 Cumplimiento de Requerimientos

✅ **Sistema distribuido** con microservicios  
✅ **API Gateway** implementado  
✅ **3+ entidades** (Pacientes, Doctores, Citas)  
✅ **Relaciones complejas** entre entidades  
✅ **CRUD completo** en todas las entidades  
✅ **Validaciones avanzadas** con reglas de negocio  
✅ **Búsqueda por múltiples criterios**  
✅ **Containerización** con Docker  
✅ **Pruebas funcionales** con Postman  

## 👩‍💻 Autora

**Susana Eguis Muñoz**  
Proyecto Universitario - Sistemas Distribuidos  
Fecha: Junio 2025

---

**¿Problemas o preguntas?** Revisar la sección de solución de problemas o verificar que todos los servicios estén corriendo correctamente.
