# Arquitectura Hexagonal (Puertos y Adaptadores)

## Visión General

Este proyecto sigue el patrón de **Arquitectura Hexagonal** (también conocido como Puertos y Adaptadores), que separa la lógica de negocio del dominio de los detalles de implementación externos.

## Estructura por Módulos

```
schedule-generator-api/
├── courses/                    # Módulo de Cursos
│   ├── domain/                 # 🔷 DOMINIO (Core)
│   │   ├── model/              # Entidades del dominio
│   │   │   └── course.py       # Course, CourseAvailability
│   │   └── ports/              # Interfaces (contratos)
│   │       └── courses_repository.py  # CourseRepository (puerto)
│   ├── application/            # 🔶 APLICACIÓN (Casos de uso)
│   │   ├── course.py           # CourseService (orquestación)
│   │   └── course_filter/      # Lógica de filtrado
│   └── infrastructure/         # 🔧 INFRAESTRUCTURA (Adaptadores)
│       └── mongo_courses_repository.py  # MongoCourseRepository (adaptador)
│
├── schedules/                  # Módulo de Horarios
│   ├── domain/                 # 🔷 DOMINIO
│   │   ├── model/              # Entidades del dominio
│   │   │   └── schedule.py     # Schedule
│   │   └── ports/              # Interfaces
│   │       └── schedule_scraper_port.py  # ScheduleScraperPort (puerto)
│   ├── application/            # 🔶 APLICACIÓN
│   │   ├── schedule.py         # ScheduleService (casos de uso)
│   │   └── scraper_service.py  # SAESScraperService (adaptador en application por legacy)
│   └── infrastructure/         # 🔧 INFRAESTRUCTURA
│       └── (futuros adaptadores)
│
├── routes/                     # 🌐 INTERFACES DE ENTRADA (Adaptadores REST)
│   ├── schedule.py             # Endpoints de horarios
│   ├── course.py               # Endpoints de cursos
│   ├── login.py                # Endpoints de autenticación
│   └── teacher.py              # Endpoints de profesores
│
└── schemas/                    # 📋 DTOs para la capa de presentación
    ├── schedule.py             # Schemas de request/response
    └── login.py                # Schemas de autenticación
```

## 🔷 Capa de Dominio (Core)

**Responsabilidad**: Contiene la lógica de negocio pura, sin dependencias externas.

### Entidades (Models)
Objetos del dominio con lógica de negocio:
- `Course`: Representa un curso con horarios, profesor, disponibilidad
- `Schedule`: Representa un horario generado
- `CourseAvailability`: Disponibilidad de un curso

### Puertos (Ports - Interfaces)
Contratos que definen cómo el dominio se comunica con el exterior:

#### `CourseRepository` (Puerto de salida)
```python
class CourseRepository(ABC):
    @abstractmethod
    def get_courses(...) -> List[Course]: pass
    
    @abstractmethod
    def upsert_course(course: Course) -> bool: pass
    
    @abstractmethod
    def insert_courses(courses: List[Course]) -> int: pass
    
    @abstractmethod
    def update_course_availability(...) -> bool: pass
    
    @abstractmethod
    def get_downloaded_periods(...) -> Dict[str, float]: pass
    
    @abstractmethod
    def set_downloaded_periods(...) -> None: pass
    
    @abstractmethod
    def check_missing_periods(...) -> List[int]: pass
```

**Propósito**: Define cómo persistir y recuperar cursos sin depender de MongoDB, PostgreSQL, o cualquier tecnología específica.

#### `ScheduleScraperPort` (Puerto de salida)
```python
class ScheduleScraperPort(ABC):
    @abstractmethod
    def download_schedules(...) -> List[Dict[str, Any]]: pass
    
    @abstractmethod
    def download_availability(...) -> List[Dict[str, Any]]: pass
```

**Propósito**: Define cómo obtener horarios de sistemas externos sin depender de SAES, APIs REST, o cualquier fuente específica.

## 🔶 Capa de Aplicación (Use Cases)

**Responsabilidad**: Orquesta casos de uso del negocio usando puertos del dominio.

### Servicios de Aplicación

#### `CourseService`
```python
class CourseService:
    def __init__(self, course_repository: CourseRepository):
        self.course_repository = course_repository  # Inyección de dependencias
    
    def get_courses(...) -> List[Course]:
        """Caso de uso: Obtener cursos filtrados"""
        
    def upload_courses(courses: List[Course]) -> int:
        """Caso de uso: Guardar cursos descargados"""
        
    def check_missing_periods(...) -> List[int]:
        """Caso de uso: Verificar períodos a descargar"""
```

**Características**:
- Depende de `CourseRepository` (puerto), no del adaptador concreto
- Orquesta lógica de negocio (filtros, validaciones)
- No sabe si los datos vienen de MongoDB, SQL, o API externa

#### `ScheduleService`
```python
class ScheduleService:
    def generate_schedules(...) -> List[Schedule]:
        """Caso de uso: Generar horarios válidos"""
```

## 🔧 Capa de Infraestructura (Adaptadores)

**Responsabilidad**: Implementa los puertos con tecnologías específicas.

### Adaptadores de Persistencia

#### `MongoCourseRepository` (implementa `CourseRepository`)
```python
class MongoCourseRepository(CourseRepository):
    """Adaptador de persistencia usando MongoDB"""
    
    def __init__(self):
        self.mongo_client = MongoClient(...)
        self.database = self.mongo_client[...]
        self.course_collection = self.database['courses']
    
    def get_courses(...) -> List[Course]:
        # Implementación específica de MongoDB
        results = self.course_collection.find(...)
        return [Course(**doc) for doc in results]
    
    def upsert_course(self, course: Course) -> bool:
        # Usa operaciones de MongoDB (update_one con upsert=True)
        ...
```

**Ventaja**: Se puede reemplazar por `PostgresCourseRepository` o `InMemoryCourseRepository` sin cambiar el dominio.

### Adaptadores de Scrapers

#### `SAESScraperService` (implementa `ScheduleScraperPort`)
```python
class SAESScraperService(ScheduleScraperPort):
    """Adaptador de scraping para sistema SAES usando Selenium"""
    
    def download_schedules(...) -> List[Dict[str, Any]]:
        # Usa Selenium + Firefox para scraping
        self.driver = webdriver.Firefox(...)
        # Navega, parsea HTML, retorna datos
```

**Ventaja**: Se puede agregar `SAESAPIAdapter` (si SAES tuviera API) o `MockScraperAdapter` para testing.

## 🌐 Interfaces de Entrada (REST API)

### Endpoints (Adaptadores de entrada)

#### `routes/schedule.py`
```python
@router.post('/schedules/download')
async def download_schedules_endpoint(request: ScheduleDownloadRequest):
    # 1. Valida sesión (autenticación)
    # 2. Crea adaptador de scraper
    scraper = SAESScraperService(session_id, token)
    
    # 3. Usa servicio de aplicación
    course_service = CourseService(MongoCourseRepository())
    missing_periods = course_service.check_missing_periods(...)
    
    # 4. Orquesta descarga
    if missing_periods:
        courses = scraper.download_schedules(...)
        course_service.upload_courses(courses)
```

**Responsabilidad**:
- Validar requests HTTP
- Convertir DTOs (schemas) a entidades del dominio
- Orquestar servicios de aplicación
- Retornar responses HTTP

## 📦 Inyección de Dependencias

### Patrón actual
```python
# En routes/schedule.py
course_service = CourseService(router.courses)  # router.courses es MongoCourseRepository
scraper = SAESScraperService(session_id, token)
```

### Mejora sugerida (Dependency Injection Container)
```python
# En main.py o config
def configure_dependencies():
    course_repo = MongoCourseRepository()
    schedule_scraper = SAESScraperService()
    
    course_service = CourseService(course_repo)
    schedule_service = ScheduleService(course_service)
    
    return {
        'course_service': course_service,
        'schedule_service': schedule_service,
        'schedule_scraper': schedule_scraper
    }

# En routes
deps = configure_dependencies()
course_service = deps['course_service']
```

## 🎯 Beneficios de la Arquitectura Hexagonal

### 1. Independencia de Frameworks
- El dominio no depende de FastAPI, Flask, o Django
- Se puede cambiar el framework web sin tocar la lógica de negocio

### 2. Independencia de Base de Datos
- El dominio no conoce MongoDB
- Se puede migrar a PostgreSQL cambiando solo el adaptador

### 3. Testeable
```python
# Test unitario con mock repository
def test_get_courses():
    mock_repo = MockCourseRepository()
    service = CourseService(mock_repo)
    courses = service.get_courses(...)
    assert len(courses) == 10
```

### 4. Mantenible
- Cambios en scrapers no afectan al dominio
- Cambios en la API no afectan a la lógica de negocio
- Cada capa tiene responsabilidad única

### 5. Escalable
- Fácil agregar nuevos adaptadores (APIs, otras fuentes)
- Fácil agregar nuevos casos de uso sin romper existentes

## 🔄 Flujo de Datos (Ejemplo)

```
HTTP Request
    ↓
[FastAPI Route] (Adaptador de entrada)
    ↓
[ScheduleDownloadRequest] (DTO/Schema)
    ↓
[CourseService] (Aplicación)
    ↓
[CourseRepository Port] (Interfaz)
    ↓
[MongoCourseRepository] (Adaptador de salida)
    ↓
[MongoDB]

HTTP Request
    ↓
[FastAPI Route]
    ↓
[SAESScraperService] (Adaptador - implementa ScheduleScraperPort)
    ↓
[Selenium + Firefox]
    ↓
[SAES Website HTML]
    ↓
[CourseService] (Aplicación - persiste)
    ↓
[MongoCourseRepository]
    ↓
[MongoDB]
```

## 📚 Conceptos Clave

### Puerto (Port)
- Interfaz (clase abstracta) que define un contrato
- Vive en `domain/ports/`
- Ejemplos: `CourseRepository`, `ScheduleScraperPort`

### Adaptador (Adapter)
- Implementación concreta de un puerto
- Vive en `infrastructure/` o maneja I/O externo
- Ejemplos: `MongoCourseRepository`, `SAESScraperService`

### Servicio de Aplicación (Application Service)
- Orquesta casos de uso del negocio
- Usa puertos (no adaptadores directamente)
- Vive en `application/`
- Ejemplos: `CourseService`, `ScheduleService`

### Entidad de Dominio (Domain Entity)
- Objeto con identidad y lógica de negocio
- Vive en `domain/model/`
- Ejemplos: `Course`, `Schedule`

## 🚀 Próximos Pasos de Arquitectura

1. **Mover `SAESScraperService` a `schedules/infrastructure/`**
   - Actualmente está en `application/` por razones históricas

2. **Crear `ScheduleRepository` port**
   - Para persistir horarios generados

3. **Implementar Dependency Injection Container**
   - Usar `dependency-injector` o FastAPI's `Depends`

4. **Agregar más tests unitarios**
   - Usar mocks de puertos para tests rápidos

5. **Documentar casos de uso**
   - Crear diagramas de secuencia por caso de uso
