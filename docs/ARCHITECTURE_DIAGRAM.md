# Arquitectura Hexagonal - Diagrama Visual

## Vista General del Sistema

```
                            ┌─────────────────────────────────────┐
                            │         Cliente HTTP/Web            │
                            └──────────────┬──────────────────────┘
                                           │
                                           ↓
╔══════════════════════════════════════════════════════════════════════╗
║                    🌐 ADAPTADORES DE ENTRADA (REST API)              ║
║                                                                      ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              ║
║  │  /schedules  │  │   /courses   │  │    /login    │              ║
║  │              │  │              │  │              │              ║
║  │ - download() │  │ - get()      │  │ - login()    │              ║
║  │ - generate() │  │ - filter()   │  │ - captcha()  │              ║
║  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              ║
║         │                  │                  │                      ║
╚═════════╪══════════════════╪══════════════════╪══════════════════════╝
          │                  │                  │
          │  ┌───────────────┴──────────────────┘
          │  │
          ↓  ↓
╔══════════════════════════════════════════════════════════════════════╗
║              🔶 CAPA DE APLICACIÓN (Casos de Uso)                    ║
║                                                                      ║
║  ┌─────────────────────────────┐  ┌──────────────────────────────┐  ║
║  │     ScheduleService         │  │      CourseService           │  ║
║  │                             │  │                              │  ║
║  │ - generate_schedules()      │  │ - get_courses()              │  ║
║  │ - validate_schedule()       │  │ - filter_courses()           │  ║
║  │                             │  │ - upload_courses()           │  ║
║  │                             │  │ - check_missing_periods()    │  ║
║  └──────────────┬──────────────┘  └──────────┬───────────────────┘  ║
║                 │                             │                      ║
╚═════════════════╪═════════════════════════════╪══════════════════════╝
                  │                             │
                  │    ┌────────────────────────┘
                  │    │
                  ↓    ↓
╔══════════════════════════════════════════════════════════════════════╗
║                  🔷 DOMINIO (Lógica de Negocio)                      ║
║                                                                      ║
║  ┌──────────────────┐        ┌─────────────────────────────────┐   ║
║  │   Entidades      │        │   Puertos (Interfaces)          │   ║
║  │                  │        │                                 │   ║
║  │ • Course         │        │ • CourseRepository              │   ║
║  │ • Schedule       │        │   - get_courses()               │   ║
║  │ • Teacher        │        │   - insert_courses()            │   ║
║  │ • Subject        │        │   - upsert_course()             │   ║
║  │                  │        │   - update_availability()       │   ║
║  │                  │        │   - get_downloaded_periods()    │   ║
║  │                  │        │                                 │   ║
║  │                  │        │ • ScheduleScraperPort           │   ║
║  │                  │        │   - download_schedules()        │   ║
║  │                  │        │   - download_availability()     │   ║
║  └──────────────────┘        └──────────────┬──────────────────┘   ║
║                                              │                      ║
╚══════════════════════════════════════════════╪══════════════════════╝
                                               │ implementado por
                                               ↓
╔══════════════════════════════════════════════════════════════════════╗
║            🔧 ADAPTADORES DE SALIDA (Infraestructura)                ║
║                                                                      ║
║  ┌──────────────────────────┐    ┌─────────────────────────────┐   ║
║  │  MongoCourseRepository   │    │   SAESScraperService        │   ║
║  │  (implementa             │    │   (implementa               │   ║
║  │   CourseRepository)      │    │    ScheduleScraperPort)     │   ║
║  │                          │    │                             │   ║
║  │ • Conexión MongoDB       │    │ • Selenium + Firefox        │   ║
║  │ • Queries con pymongo    │    │ • HTML parsing              │   ║
║  │ • Índices y agregaciones │    │ • Cookie management         │   ║
║  │ • Cache metadata         │    │ • Navigation automation     │   ║
║  └──────────┬───────────────┘    └──────────┬──────────────────┘   ║
║             │                                │                      ║
╚═════════════╪════════════════════════════════╪══════════════════════╝
              │                                │
              ↓                                ↓
     ┌─────────────────┐           ┌──────────────────────┐
     │    MongoDB      │           │   SAES Website       │
     │   (Database)    │           │   (Sistema Legacy)   │
     └─────────────────┘           └──────────────────────┘
```

## Flujo de una Request: POST /schedules/download

```
1. Cliente HTTP
   │
   ├─→ POST /schedules/download
   │   Body: { session_id, career, plan, periods }
   │
   ↓
2. 🌐 Adaptador de Entrada (routes/schedule.py)
   │
   ├─→ Valida request (ScheduleDownloadRequest schema)
   ├─→ Verifica sesión en login_store
   ├─→ Crea instancia de CourseService
   │
   ↓
3. 🔶 Capa de Aplicación (CourseService)
   │
   ├─→ check_missing_periods(career, plan, periods)
   │   │
   │   ├─→ Llama a CourseRepository.get_downloaded_periods()
   │   │   (puerto - no sabe que es MongoDB)
   │   │
   │   └─→ Calcula: missing_periods = [4, 5] (ejemplo)
   │
   ↓
4. Si hay períodos faltantes:
   │
   ├─→ 🔧 Adaptador de Salida (SAESScraperService)
   │   │
   │   ├─→ download_schedules(periods=[4,5])
   │   │   • Inicia Selenium + Firefox
   │   │   • Navega a SAES con cookies
   │   │   • Parsea tablas HTML
   │   │   • Retorna: List[Dict] con cursos
   │   │
   │   └─→ download_availability()
   │       • Similar proceso para disponibilidad
   │
   ↓
5. 🔶 Aplicación: CourseService.upload_courses()
   │
   ├─→ Convierte Dict → Course (entidad dominio)
   ├─→ Llama a CourseRepository.insert_courses(courses)
   │   │
   │   └─→ 🔧 MongoCourseRepository.insert_courses()
   │       • Itera cursos
   │       • upsert_course() en MongoDB
   │       • Retorna: count guardados
   │
   ↓
6. 🔶 Aplicación: set_downloaded_periods()
   │
   └─→ CourseRepository.set_downloaded_periods([4,5], timestamp)
       │
       └─→ 🔧 MongoDB: update course_metadata collection
   
   ↓
7. 🌐 Adaptador de Entrada
   │
   ├─→ Construye ScheduleDownloadResponse
   └─→ Retorna HTTP 200 con JSON
```

## Ventajas del Diseño

### ✅ Testeable
```python
# Test unitario sin MongoDB real
def test_upload_courses():
    mock_repo = MockCourseRepository()  # Implementa CourseRepository
    service = CourseService(mock_repo)
    
    courses = [Course(...), Course(...)]
    count = service.upload_courses(courses)
    
    assert count == 2
    assert mock_repo.insert_courses_called
```

### ✅ Intercambiable
```python
# Cambiar de MongoDB a PostgreSQL
postgres_repo = PostgresCourseRepository()  # Nueva implementación
service = CourseService(postgres_repo)      # Mismo código de servicio
```

### ✅ Independiente
```python
# El dominio no conoce FastAPI, MongoDB, Selenium
# Solo interfaces (puertos)
class CourseRepository(ABC):
    @abstractmethod
    def get_courses(...) -> List[Course]: pass
```

## Capas y Responsabilidades

| Capa | Responsabilidad | Ejemplo |
|------|----------------|---------|
| 🌐 **Adaptadores Entrada** | HTTP, validación, serialización | `routes/schedule.py` |
| 🔶 **Aplicación** | Orquestar casos de uso | `CourseService.upload_courses()` |
| 🔷 **Dominio** | Lógica de negocio pura | `Course`, `CourseRepository` (puerto) |
| 🔧 **Adaptadores Salida** | DB, APIs, scraping | `MongoCourseRepository`, `SAESScraperService` |

## Reglas de Dependencia

```
Permitido ✅:
  Aplicación → Dominio (puertos)
  Adaptadores → Dominio (implementan puertos)
  Adaptadores Entrada → Aplicación

Prohibido ❌:
  Dominio → Aplicación
  Dominio → Adaptadores
  Aplicación → Adaptadores directamente (debe usar puertos)
```

## Ejemplo de Violación vs Correcto

### ❌ Violación (acoplamiento directo)
```python
class CourseService:
    def __init__(self):
        # Acoplado a MongoDB directamente
        self.mongo = MongoClient("mongodb://...")
    
    def get_courses(self):
        return self.mongo.db.courses.find(...)
```

### ✅ Correcto (usa puerto)
```python
class CourseService:
    def __init__(self, course_repository: CourseRepository):
        # Depende de interfaz, no implementación
        self.course_repository = course_repository
    
    def get_courses(self):
        return self.course_repository.get_courses(...)
```

## Puntos de Extensión

### Agregar nuevo adaptador de scraping
```python
# 1. Implementar el puerto
class APIScraperService(ScheduleScraperPort):
    def download_schedules(...):
        response = requests.get("https://api.saes....")
        return response.json()

# 2. Usar en el endpoint
scraper = APIScraperService()  # En lugar de SAESScraperService
```

### Agregar nuevo repositorio
```python
# 1. Implementar el puerto
class RedisCourseRepository(CourseRepository):
    def get_courses(...):
        # Implementación con Redis
        
# 2. Inyectar en servicio
service = CourseService(RedisCourseRepository())
```

### Testing con mocks
```python
class MockCourseRepository(CourseRepository):
    def __init__(self):
        self.courses = []
    
    def insert_courses(self, courses):
        self.courses.extend(courses)
        return len(courses)

# Test sin MongoDB
repo = MockCourseRepository()
service = CourseService(repo)
```
