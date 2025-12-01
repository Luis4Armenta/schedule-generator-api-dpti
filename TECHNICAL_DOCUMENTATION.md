# Documentación técnica — schedule-generator-api

Última actualización: 30/11/2025

Propósito
--------
Esta documentación técnica describe con detalle la arquitectura, módulos, flujos, dependencias, técnicas y recomendaciones del backend "schedule-generator-api". Está pensada para desarrolladores que hereden el proyecto, para evaluadores académicos y para quien deba desplegar o mantener el servicio.

Contenido
--------
- Visión general
- Estructura del repositorio
- Arquitectura y patrones usados
- Módulos clave (descripción por carpeta)
- Contratos y puertos (interfaces)
- Persistencia y estrategia MongoDB
- Scraper SAES y manejo de CAPTCHA
- Servicios de aplicación y algoritmos de generación de horarios
- Endpoints REST y modelos (schemas)
- Manejo de sesiones y seguridad mínima
- Tests, coverage y cómo reproducir pruebas
- Deploy (Docker / gunicorn / uvicorn)
- Operación y troubleshooting
- Recomendaciones y próximos pasos

Visión general
--------------
Schedule-Generator-API es un backend en Python que expone endpoints REST (FastAPI) para:

- Autenticar y mantener sesiones con el portal SAES (captcha + login)
- Descargar y parsear mapas curriculares y horarios desde SAES (scraper)
- Persistir cursos y disponibilidades en MongoDB
- Generar combinaciones válidas de horarios (algoritmo de backtracking) y puntuarlos (incluye análisis de sentimiento para profesores)

El proyecto sigue el patrón de Arquitectura Hexagonal (puertos y adaptadores) para separar dominio, casos de uso y detalles de infraestructura.

Estructura del repositorio (resumen)
----------------------------------
Raíz del repo (archivos y carpetas relevantes):

- `main.py` — arranque de la aplicación FastAPI, configuración de routers y middleware.
- `routes/` — adaptadores de entrada: endpoints REST (schedule.py, captcha.py, login.py).
- `schemas/` — modelos Pydantic (DTOs) usados por endpoints.
- `courses/` — módulo de cursos (dominio, aplicación, infraestructura).
  - `courses/domain/` — entidades (Course) y puertos (`courses_repository`).
  - `courses/application/` — `CourseService`, lógica para manejo de cursos.
  - `courses/infrastructure/` — `MongoCourseRepository` (adaptador de salida a MongoDB).
- `schedules/` — módulo de horarios.
  - `schedules/domain/` — entidad Schedule y puertos de scraper.
  - `schedules/application/` — `ScheduleService` (generador) y `scraper_service` (SAES wrapper).
- `teachers/` — (estructura preparada para repositorio/proveedor de profesores y servicios asociados).
- `utils/` — utilidades (text cleaning, enums, helpers).
- `tests/` — suite de pruebas (pytest) con tests unitarios e integración simulada.
- `docs/` — documentación de alto nivel (arquitectura, persistencia, uso de CAPTCHA, etc.).
- `data/` — directorio que contiene archivos de MongoDB (WiredTiger). En general no debería versionarse con el código.

Arquitectura y patrones
-----------------------
El proyecto aplica la Arquitectura Hexagonal (Ports & Adapters):

- Entradas: `routes/*` (FastAPI routers) que actúan como adaptadores de entrada.
- Aplicación: `*application*` — casos de uso y servicios (`CourseService`, `ScheduleService`).
- Dominio: `*domain*` — entidades y reglas del dominio (Course, Schedule).
- Salidas/Infraestructura: `*infrastructure*` — adaptadores concretos (Mongo repository, SAES scraper) que implementan los puertos definidos en `domain/ports`.

Beneficios:
- Facilita testing: los servicios y dominio pueden probarse con mocks de los puertos.
- Permite intercambiar adaptadores (e.g., otro repositorio o scraper) sin cambiar la lógica de negocio.

Módulos clave (detalle)
-----------------------

main.py
^^^^^^^
- Inicializa FastAPI, añade middlewares, y registra routers (schedule, captcha, login).
- Durante `startup` instancia `MongoCourseRepository()` y la conecta; lo asigna a `app.courses` para que los routers lo usen.
- Expone `/` como mensaje de bienvenida.

routes/captcha.py
^^^^^^^^^^^^^^^^^
- Endpoints relacionados a la extracción de captcha:
  - `GET /captcha` — solicita la página SAES, extrae el div del captcha, descarga la imagen, codifica en base64, extrae campos ocultos y devuelve `session_id` + metadatos.
  - `GET /captcha/refresh` — wrapper que llama `get_captcha` para refrescar.
  - `GET /captcha/status` — chequea si SAES responde (health check simple).
- Mantiene `captcha_store` (in-memory) con TTL (configurado como 300s) para asociar `session_id` con cookies y hidden fields.

routes/login.py
^^^^^^^^^^^^^^^
- Endpoint `POST /login` — realiza login en SAES usando boleta, password, captcha code y hidden fields.
- Flujo:
  1. Recupera `stored` desde `captcha_store` por `session_id` o usa valores enviados en el body como fallback.
  2. Realiza `session.post` al `default.aspx` con form data que incluye campos ocultos.
  3. Comprueba si el login devolvió mensaje de error en el HTML.
  4. Si está ok, accede a `mapa_curricular.aspx` y recorre selects de carrera/plan/periodos, haciendo POSTs sucesivos para obtener planes y periodos por carrera.
  5. Extrae cookies de autenticación (ASP.NET_SessionId, .ASPXFORMSAUTH) y guarda un `login_store` en memoria con TTL (30 minutos).
  6. Emite cookie httpOnly `saes_session_id` para el cliente.

routes/schedule.py
^^^^^^^^^^^^^^^^^^
- Endpoints principales para generación y descarga de horarios:
  - `POST /schedules/` — genera combinaciones válidas de horarios usando `ScheduleService` y `CourseService`.
  - `POST /schedules/download` — descarga horarios desde SAES (requiere `session_id` de login). Implementa cache semanal: descarga completa cada 7 días, y solo actualiza disponibilidad entre descargas.
  - `POST /schedules/download-availability` — descarga únicamente disponibilidades.
- El endpoint de descarga orquesta: verifica sesión, determina periodos faltantes, inicializa `SAESScraperService` con cookies/token, descarga cursos y disponibilidades, guarda cursos en Mongo y retorna lista resumida.

schemas/
^^^^^^^^
- Modelos Pydantic que definen requests y responses para endpoints: `captcha.py`, `login.py`, `schedule.py`.
- Usados por FastAPI para validación automática y documentación OpenAPI.

courses/*
^^^^^^^^^
- `Course` entity model
- `CourseService` (application): lógica para obtener cursos, validar periodos descargados, subir cursos a Mongo, actualizar disponibilidades, etc.
- `MongoCourseRepository` (infrastructure): implementación concreta que usa `pymongo` para persistir cursos y registros de periodos descargados.

schedules/*
^^^^^^^^^^^^
- `ScheduleService`: algoritmo que genera combinaciones válidas de horarios (backtracking), aplica filtros (turnos, horas, semestres, créditos, exclusiones) y puntúa horarios (incluye métricas como puntaje del profesor).
- `SAESScraperService`: wrapper que implementa la lógica de scraping (Selenium o requests según implementación) para descargar horarios y disponibilidades. En la documentación se detalla que en producción se usa Selenium + Firefox headless.

teachers/*
^^^^^^^^^^^
- Estructura preparada para manejar lógica y repositorio de profesores. Algunos tests apuntan a módulos en `teachers` — revisar su implementación o stubs.

utils/*
^^^^^^^
- `utils/text.py`: funciones para limpieza y normalización de nombres, generación de regex para matching de turnos/semestres.
- `utils/enums.py`: enumeraciones (Tags, etc.).

Contratos y puertos (interfaces)
-------------------------------
El proyecto define interfaces (puertos) para permitir sustitución de adaptadores:

- `courses.domain.ports.courses_repository.CourseRepository` — contracto para persistencia de cursos (get, upload, update_availability, set_downloaded_periods, check_missing_periods).
- `schedules.domain.ports.schedule_scraper_port.ScheduleScraperPort` — contrato para descargar schedules y disponibilidades desde SAES.

Implementaciones actuales:
- `courses.infrastructure.mongo_courses_repository.MongoCourseRepository` implements CourseRepository (usa `pymongo`).
- `schedules.application.scraper_service.SAESScraperService` implements ScheduleScraperPort (usa requests/Selenium internamente).

Persistencia y estrategia MongoDB
---------------------------------
La persistencia principal es MongoDB (driver `pymongo`). Notas importantes:

- `MongoCourseRepository` guarda documentos de cursos y mantiene una colección/meta para períodos descargados con timestamps para implementar la cache semanal.
- El repo incluye datos de una instancia de MongoDB en `data/` (WiredTiger files). Estos no deberían versionarse en Git; en CI/entornos de desarrollo se recomienda usar una instancia de MongoDB local o un mock de `pymongo`.
- Recomendaciones: para pruebas de integración usar una instancia temporal (mongomock o Docker Mongo). Para producción, desplegar Mongo con backups y autenticación.

Scraper SAES y manejo de CAPTCHA
--------------------------------
El scraping del SAES implica varios retos:

- Protección con captcha (imagen) en la página principal. El flujo implementado es:
  1. Obtener `/` de SAES, extraer div del captcha e imagen (base64), extraer campos ocultos (`__VIEWSTATE`, `__EVENTVALIDATION`, etc.) y cookies de sesión.
  2. El cliente resuelve el captcha visualmente y envía la respuesta a `POST /login` junto con `session_id` retornado.
  3. `POST /login` rehace la sesión con cookies y fields, envía credenciales y captcha, y extrae la página de mapa curricular.

- Implementación técnica: `requests.Session` con headers que simulan navegador. En ambientes que requieren ejecutar JS o obtener recursos dinámicos, se usa Selenium + Firefox headless (documentado en README).

Consideraciones legales y éticas: el scraping de portales de terceros puede violar términos de servicio. Asegúrate de contar con permisos y de respetar políticas del SAES antes de automatizar en producción.

Servicios de aplicación y algoritmos
----------------------------------
Schedule generation (ScheduleService):

- Algoritmo: backtracking que recorre combinaciones de secciones/cursos respetando restricciones (horarios, turnos, créditos, semestres, exclusiones y requisitos).
- Para cada horario candidato se calcula una puntuación que incorpora métricas de preferencia (por ejemplo puntaje positivo de profesores derivado de análisis de sentimiento de comentarios).
- El servicio permite limitar resultados (`max_results`), número de asignaturas (`length`), filtros por turno/horario, y exclusiones.

Puntos de optimización y escalabilidad:
- Podrías paralelizar la exploración de ramas del backtracking en procesos/threads o usar heurísticas (order by most constrained variable) para reducir espacio de búsqueda.
- Memorizar subsoluciones o aplicar poda adicional basada en incompatibilidades de tiempo puede mejorar rendimiento.

API REST — Endpoints principales
--------------------------------

- GET / — home (HTML simple)
- GET /captcha — devuelve `session_id`, imagen en base64, campos ocultos y cookies para resolver captcha
- GET /captcha/refresh — refresca el captcha
- GET /captcha/status — health check contra SAES
- POST /login — realiza login en SAES y devuelve `carrera_info` y `session_id` autenticado
- POST /schedules/ — genera horarios a partir de parámetros (request model `ScheduleGeneratorRequest`)
- POST /schedules/download — descarga cursos desde SAES (requiere `session_id` de login)
- POST /schedules/download-availability — descarga solo disponibilidades

Para ver los schemas exactos y ejemplos, revisa `schemas/*.py`.

Seguridad y manejo de sesiones
------------------------------
- Sesiones temporales:
  - `captcha_store` guarda datos del captcha (hidden fields, cookies) por ~5 minutos.
  - `login_store` guarda cookies autenticadas por ~30 minutos.
- La implementación actual guarda estas sesiones en memoria (dentro del proceso Gunicorn). Esto es frágil ante reinicios de workers o despliegues. Recomendaciones:
  - Persistir sesiones en Redis o Mongo para alta disponibilidad entre workers.
  - Asegurar que cookies sensibles no se expongan en logs ni en respuestas públicas.
- Cookies: se emite `saes_session_id` como cookie httpOnly para el cliente.

Tests y cobertura
-----------------
- Framework: pytest.
- Se añadieron pruebas unitarias y de integración simulada que cubren endpoints `captcha`, `login` y la lógica de filtros/servicios.
- Para la entrega se generó un coverage report: cobertura total ~70% (informes en `reports/coverage_html`).
- `scripts/run_tests.sh` ejecuta tests y guarda salida en `tests/results.txt`.

Cómo ejecutar tests y coverage (reproducible)
-------------------------------------------
Desde la raíz del repo:

```bash
# crear/activar venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# ejecutar tests y guardar salida
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh

# ejecutar coverage (genera reports/coverage_html)
.venv/bin/python -m pytest --cov=. --cov-report=html:reports/coverage_html --cov-report=term
```

Despliegue y configuración
---------------------------
- Docker: el repo incluye `Dockerfile` y `docker-compose.yml` para orquestar la app y dependencias (MongoDB). Revisa las variables de entorno en `.env copy` y ajústalas.
- Gunicorn: `gunicorn.conf.py` contiene settings (timeout 180s) pensados para tareas largas (scraping). En producción, configurar workers y timeouts según la carga.
- Recomendaciones de producción:
  - Ejecutar scraper en un worker separado o servicio asíncrono (cola de tareas) para no bloquear request-response del API.
  - Usar Redis para sesiones y cachés.
  - Asegurar TLS/HTTPS y políticas de CORS adecuadas (FastAPI ya añade CORSMiddleware en `main.py`).

Operación y troubleshooting
--------------------------
Problemas frecuentes y cómo abordarlos:

- PyTest recolecta archivos grandes en `data/` (WiredTiger) y puede fallar con PermissionError. Mitigación: ignorar `data/` en pytest o mover esos archivos fuera del repo.
- Sesiones perdidas tras reinicio de worker -> 401 en descarga: persistir sesiones en Redis o Mongo.
- Scraper falla por cambios en HTML del SAES: mantener selectores en un solo lugar y añadir tests que verifiquen parsing con fixtures HTML.

Instrumentación y logging
-------------------------
- Registrar eventos clave con niveles: INFO para pasos de orquestación (inicio de descarga), WARNING para situaciones recuperables, ERROR para excepciones.
- Registrar tiempos (duración de descarga, generación de horarios) para identificar cuellos de botella.
- Guardar trazas de errores en un sistema central (ELK, Azure Monitor, etc.) para posterior análisis.

Mejoras y próximos pasos
------------------------
Prioritarias:
- Persistir `captcha_store` y `login_store` fuera del proceso (Redis/Mongo) para resiliencia.
- Implementar fixtures reutilizables en `tests/conftest.py` para stubs del scraper y repositorio y así mejorar coverage de adaptadores.
- Añadir tests que cubran `routes/schedule.py` y `schedules/application/scraper_service.py` con mocks para Selenium/pymongo.

Medio plazo / opcionales:
- Paralelizar o reescribir la generación de horarios con heurísticas para mejorar rendimiento.
- Añadir un pipeline CI (GitHub Actions) que ejecute tests, genere coverage y suba artefactos (JUnit XML, coverage HTML).
- Documentar un proceso de despliegue en Kubernetes con despliegue separado para workers de scraping.

Anexos
------
- Documentación de alto nivel en `docs/` (ARCHITECTURE_DIAGRAM.md, MONGODB_PERSISTENCE.md, CAPTCHA_USAGE.md).
- Test evidence: `tests/results.txt`, `tests/coverage_results.txt`, y `reports/coverage_html/index.html`.

Contacto y responsables
-----------------------
Para dudas técnicas sobre el diseño/implementación, contactar al autor del repositorio (ver historia de commits) o revisar `docs/IMPLEMENTATION_SUMMARY.md`.

Fin del documento.
