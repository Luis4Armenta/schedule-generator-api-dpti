# Generador de horarios UPIICSA API

API desarrollada en **FastAPI** que emplea web scraping para extraer horarios del SAES (Sistema de Administración Escolar) y genera combinaciones óptimas de horarios basándose en análisis de sentimiento de comentarios sobre profesores.

## 📚 Documentación

Toda la documentación técnica está organizada en la carpeta [`docs/`](docs/):

### Arquitectura
- **[Diagrama de Arquitectura Visual](docs/ARCHITECTURE_DIAGRAM.md)**: Diagramas visuales y flujos completos del sistema
- **[Arquitectura Hexagonal](docs/HEXAGONAL_ARCHITECTURE.md)**: Descripción completa del patrón de puertos y adaptadores

### Implementación
- **[Persistencia MongoDB](docs/MONGODB_PERSISTENCE.md)**: Estrategia de cache granular por período
- **[Diagrama de Flujo](docs/FLOW_DIAGRAM.md)**: Flujos visuales del sistema de descarga
- **[Resumen de Implementación](docs/IMPLEMENTATION_SUMMARY.md)**: Cambios y decisiones técnicas

### Integración
- **[Uso de CAPTCHA](docs/CAPTCHA_USAGE.md)**: Manejo de autenticación con SAES

## 🏗️ Arquitectura

Este proyecto sigue el patrón de **Arquitectura Hexagonal** (Puertos y Adaptadores):

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 API REST (FastAPI)                    │
│                   Adaptadores de Entrada                    │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              🔶 Capa de Aplicación (Use Cases)              │
│         CourseService, ScheduleService                      │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│               🔷 Dominio (Lógica de Negocio)                │
│    Course, Schedule + CourseRepository (puerto)             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│          🔧 Infraestructura (Adaptadores de Salida)         │
│     MongoCourseRepository, SAESScraperService               │
└─────────────────────────────────────────────────────────────┘
```

Ver [docs/HEXAGONAL_ARCHITECTURE.md](docs/HEXAGONAL_ARCHITECTURE.md) para detalles completos.

## Características

- ✅ Extrae horarios de clase desde SAES usando Selenium + Firefox headless
- ✅ Cache inteligente por período (7 días) para optimizar descargas
- ✅ Genera todas las combinaciones válidas de horarios con algoritmo de backtracking
- ✅ Análisis de sentimiento sobre comentarios de profesores
- ✅ Puntuación y ordenamiento de horarios según preferencias
- ✅ Persistencia en MongoDB con estrategia de actualización granular
- ✅ Arquitectura hexagonal para mantenibilidad y testing

## 📂 Estructura del Proyecto

```
schedule-generator-api/
├── 📄 README.md                    # Este archivo
├── 📁 docs/                        # 📚 Documentación técnica completa
│   ├── README.md                   # Índice de documentación
│   ├── HEXAGONAL_ARCHITECTURE.md  # Arquitectura del sistema
│   ├── ARCHITECTURE_DIAGRAM.md    # Diagramas visuales
│   ├── MONGODB_PERSISTENCE.md     # Estrategia de persistencia
│   ├── FLOW_DIAGRAM.md            # Flujos de descarga
│   ├── CAPTCHA_USAGE.md           # Autenticación SAES
│   └── IMPLEMENTATION_SUMMARY.md  # Historial de cambios
├── 📁 courses/                     # Módulo de cursos
│   ├── domain/                     # Lógica de negocio
│   ├── application/                # Casos de uso
│   └── infrastructure/             # Adaptadores (MongoDB)
├── 📁 schedules/                   # Módulo de horarios
│   ├── domain/                     # Entidades y puertos
│   ├── application/                # Servicios y scraper
│   └── infrastructure/             # (Futuros adaptadores)
├── 📁 routes/                      # Endpoints REST API
├── 📁 schemas/                     # DTOs y validación
├── 📁 tests/                       # Tests unitarios
└── 🐳 docker-compose.yml           # Configuración Docker
```

## Instalación
### Python y PIP
Para esta instalación debes tener instalado en tu computadora la versión 3.9 de Python junto con [Python Package Index](https://pypi.org/project/pip/) (pip).

1. Si lo deseas puedes utilizar [venv](https://docs.python.org/es/3/library/venv.html) para crear un entorno virtual aislado en el que se instalaran las dependencias del proyecto y activarlo:
`$ python -m venv /path/to/new/virtual/environment`
`$ source env/bin/activate`

2. Instala las dependencias desde requirements.txt con pip.
`$ pip install -r requirements.txt `

3. Modifica las variables del archivo `.env copy` con las credenciales y direcciones de tu base de datos MongoDB y tus servicios de Azure.

4. Puedes cambiar el nombre del archivo de `.env copy` a `.env`.

5. Una vez colocadas correctamente las variables de entorno en `.env` puedes correr el servidor con uvicorn (Puedes averiguar más sobre uvicorn en su [documentación](https://www.uvicorn.org/)).
`$ uvicorn main:app --env-file .env --port 3000 --host 0.0.0.0 --reload`

6. Listo. Puedes acceder a la documentación automática de la API mediante la ruta `http://localhost:3000/docs'.

### Docker Compose
Necesitarás tener Docker compose instalado en tu computadora.\

1. Modifica las variables del archivo `.env copy` agregando tus credenciales de Azure (Puedes dejar las variables relacionadas con MongoDB como están).

2. Cambia el nomnre del archivo `.env copy` a `.env`.
3. Haz el build con Docker Compose.
`$ docker-compose build`

4. Levanta los contenedores con Docker Compose.
`$ docker-compose up`

5. Listo. Puedes acceder a la documentación automática de la API mediante la ruta `http://localhost:3000/docs'.

## Sesiones y errores 401

La API mantiene en memoria (dentro del proceso Gunicorn) estructuras simples (`login_store`, `captcha_store`) para asociar un `session_id` con la cookie autenticada del SAES y el estado del captcha. Si el proceso se reinicia (por:

- Reconstrucción/arranque de contenedor
- Cambio de código con reload
- Timeout o crash del worker durante scraping Selenium

entonces estas estructuras se vacían y cualquier petición subsecuente que use un `session_id` previo responderá 401 (no autenticado). Solución rápida: repetir el flujo de login para obtener un nuevo `session_id` antes de llamar a `/schedules/download`.

Para evitar pérdida de sesión podrías:

- Persistir sesiones en Redis/Mongo en lugar de memoria.
- Aumentar `timeout` de Gunicorn (ya configurado a 180s en `gunicorn.conf.py`) para reducir reinicios por tareas largas.
- Monitorear logs; si no aparecen líneas `[Schedules]` y recibes 401, probablemente el worker se reinició.

Importante: El scraping puede tardar más de 60s en periodos de alta carga del SAES; no reduzcas agresivamente el timeout.
