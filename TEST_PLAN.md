# Plan de Pruebas — schedule-generator-api

Fecha: 30/11/2025

Este documento es el plan de pruebas orientado a la entrega que debes llevar mañana. Está priorizado para que, con el tiempo limitado, puedas presentar pruebas coherentes que cubran las partes críticas del backend (endpoints REST, orquestación de servicios, y seguridad mínima). Incluye pasos rápidos para ejecutar las pruebas en tu entorno y una pequeña guía de contingencia si hay dependencias externas (Mongo, Selenium).

## Objetivos

- Verificar que los endpoints principales estén disponibles y respondan (smoke tests).
- Asegurar que los casos de uso claves (generación de horarios, descarga desde SAES) respondan correctamente ante inputs válidos y errores comunes.
- Detectar fallos bloqueantes en la capa de integración con la base de datos y adaptadores (mockear donde sea necesario para la demo).
- Proveer un conjunto reproducible de comandos para ejecutar las pruebas localmente y en la demo.

## Alcance (lo que se va a probar mañana)

- Endpoints REST principales en `routes/`:
  - `POST /schedules/` — generación de horarios (entrada mínima/smoke)
  - `POST /schedules/download` — descarga desde SAES (caso happy path con mocks)
  - `GET /captcha`, `POST /login` — sólo smoke / flujo mínimo (si ya existen y están implementados)
- Lógica de servicios:
  - `CourseService` — check_missing_periods, upload_courses, update_availability (usar mocks para Mongo)
  - `ScheduleService` — generación básica de horarios con parámetros simples
- Tests unitarios existentes (ejecutar y listar fallos)

No cubriremos mañana:

- End-to-end con Selenium real contra SAES (si no tienes acceso y configuraciones listas) — en su lugar usaremos mocks.
- Tests de rendimiento o carga.

## Prioridades y criterios de aceptación

- P0 (imprescindible para la demo):
  - Poder ejecutar `pytest` sin que falle la recolección por problemas de filesystem (p. ej. `data/`).
  - Tener 3-5 pruebas de humo que demuestren que los endpoints devuelven respuestas (usando test client o mocks).
  - Mostrar un test unitario verde para `ScheduleService.generate_schedules` (happy path).

- P1 (importante si hay tiempo):
  - Tests que validen la lógica de `download_schedules_endpoint` con el scraper mockeado (simular cookies válidas y respuesta del scraper con 2-3 cursos).
  - Tests que cubran manejo de sesiones expiradas (401) en `download_schedules_endpoint`.

- P2 (si sobra tiempo):
  - Integración ligera con una Mongo local (opcional) o pruebas que validen que `CourseService.upload_courses` es llamada correctamente mediante un mock.

## Riesgos y mitigaciones

- Archivo `data/` con permisos restringidos impide que pytest recolecte tests. Mitigación: ignorar `data/` en pytest (`pytest.ini` o `--ignore=data`). También se recomienda eliminar o mover `data/` fuera del repo si no es parte del código.
- Dependencias externas (MongoDB, Selenium) pueden no estar disponibles en tu laptop. Mitigación: usar mocks para adaptadores y crear tests que no dependan de servicios externos.

## Test matrix (resumen rápido)

- Smoke test endpoint generate schedules
  - Input: body mínimo (career, levels, semesters, start_time, end_time, length)
  - Expect: 200 OK + lista (posible vacía) o esquema `Schedule`

- Unit test ScheduleService
  - Input: parámetros simples con cursos mockeados
  - Expect: n resultados (n = length) o al menos que la función no falle

- Download schedules — sesión inexistente
  - Input: session_id inválido
  - Expect: 401

- Download schedules — happy path (con mocks)
  - Mockear `login_store` con cookies válidas y `SAESScraperService` para devolver cursos y disponibilidades
  - Expect: 200 y `total_courses` == número mockeado

## Preparación del entorno (rápida)

1. Activar el virtualenv del proyecto (si ya existe `.venv`):

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

2. Evitar que pytest recorra la carpeta `data` (solución rápida): ejecutar pytest con la opción --ignore o crear un archivo de configuración para pytest.

Recomendado (temporal):

```bash
python -m pytest --ignore=data -q
```

Recomendado (permanente): crear un archivo `pytest.ini` en la raíz con:

```ini
[pytest]
norecursedirs = data
```

> Nota: No añadas `data/` al repositorio si contiene archivos de base de datos; lo ideal es moverlo fuera y añadirlo a `.gitignore`.

## Comandos principales para la demo

- Ejecutar todos los tests (ignorando data):

```bash
python -m pytest --ignore=data -v
```

- Ejecutar sólo tests de schedules (si están marcados o ubicados en tests/schedules):

```bash
python -m pytest tests/schedules -q
```

- Ejecutar una prueba específica por nombre:

```bash
python -m pytest -k "test_nombre_parcial" -q
```

## Casos de prueba concretos (detallados) — prioridad P0

1) Smoke: GET / (home)
  - Objetivo: confirmar que la app está arrancada y la ruta base responde.
  - Método: usar `TestClient` de FastAPI o curl.
  - Entrada: GET `/`
  - Esperado: 200 y contenido HTML con 'Profesores API'

2) Unit: ScheduleService.generate_schedules (happy path)
  - Objetivo: validar que el generador no falla y produce al menos una estructura esperada cuando CourseService devuelve cursos.
  - Preparación: mockear `CourseService` para devolver 5 cursos sencillos.
  - Entrada: levels=["1"], career='A', length=3, start_time='08:00', end_time='14:00'
  - Esperado: lista de horarios con longitud <= length y sin excepciones.

3) Endpoint: download_schedules_endpoint (sesión inexistente)
  - Objetivo: validar manejo de sesión expirada o ausente
  - Preparación: request con `session_id='fake'` no presente en `login_store`
  - Entrada: body con session_id fake
  - Esperado: HTTP 401 con detalle apropiado

4) Integration-ish: download_schedules_endpoint (mock SAES)
  - Objetivo: demostrar flujo completo sin Selenium real
  - Preparación: inyectar en `router` un `login_store` con cookies válidas y reemplazar `SAESScraperService` por un stub que devuelva dos cursos y disponibilidades.
  - Entrada: body válido
  - Esperado: HTTP 200 + `total_courses` == 2 y mensaje success

## Plantillas / snippets rápidos para testear (usar en archivos `tests/`)

- Ejemplo de uso de TestClient para smoke test `/` (añadir en `tests/test_smoke.py`):

```python
from fastapi.testclient import TestClient
from main import app

def test_home_smoke():
    client = TestClient(app)
    r = client.get('/')
    assert r.status_code == 200
    assert 'Profesores API' in r.text
```

- Ejemplo de mock sencillo para `download_schedules_endpoint` (pytest + monkeypatch):

```python
def test_download_schedules_with_mock(monkeypatch):
    from routes.schedule import router
    from fastapi.testclient import TestClient
    from main import app

    # Preparar login_store con session válida
    router.login_store['test-session'] = {
        'cookies': {'ASP.NET_SessionId': 'sess', '.ASPXFORMSAUTH': 'tok'},
        'created_at': 0
    }

    # Stub del scraper
    class StubScraper:
        def __init__(self, session_id, token):
            pass
        def download_schedules(self, career, career_plan, plan_periods, shift, sequence=None):
            return [
                {'sequence': '001', 'subject': 'Mat', 'teacher': 'Profe A', 'schedule': [] , 'plan':'05','level':'1','career':'A','shift':'M','semester':'1'},
                {'sequence': '002', 'subject': 'Fis', 'teacher': 'Profe B', 'schedule': [], 'plan':'05','level':'1','career':'A','shift':'M','semester':'1'}
            ]
        def download_availability(self, career, career_plan):
            return [{'sequence':'001','subject':'Mat','availability':5},{'sequence':'002','subject':'Fis','availability':2}]

    monkeypatch.setattr('schedules.application.scraper_service.SAESScraperService', StubScraper)

    client = TestClient(app)
    body = {
        'session_id': 'test-session',
        'career': 'A',
        'career_plan': '05',
        'plan_period': ['1']
    }

    r = client.post('/schedules/download', json=body)
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'success'
    assert data['total_courses'] == 2
```

## Cronograma y estimación para la entrega (mañana)

- 0–15 min: Preparar entorno (activar venv, pip install) y confirmar `pytest --ignore=data` funciona.
- 15–45 min: Añadir 2-3 tests de humo (home, generate_schedules happy path, download_schedules mocked).
- 45–75 min: Corregir fallos de importación o ajustar mocks (p. ej. crear stubs mínimos si faltan módulos).
- 75–90 min: Ejecutar tests, corregir pequeñas fallas y preparar evidencia (capturas de salida de pytest o logs).

Si te falta tiempo: prioriza ejecutar y dejar verdes los tests P0 (smoke + 1 unit + 1 mocked integration).

## Documentación y evidencia para la presentación

- Comandos ejecutados y salida relevante de `pytest -v`.
- Pantallazos de la ejecución o logs del TestClient mostrando respuestas HTTP.
- Breve explicación (1 slide) de qué está cubierto por los tests y qué no, con razones y riesgos.

## Próximos pasos recomendados (post-demo)

1. Añadir `pytest.ini` para ignorar `data/` permanentemente en repo y/o mover `data/` fuera.
2. Implementar fakes/stubs reutilizables para `SAESScraperService` y `MongoCourseRepository` en `tests/conftest.py`.
3. Añadir CI básico (GitHub Actions) que ejecute `pytest --ignore=data` en cada PR.
4. Añadir tests adicionales para bordes: conflictos de horario, exclusión de profesores, y priorización por puntaje.

---

Si quieres, aplico ahora dos acciones rápidas y seguras que facilitan que `pytest` corra: (A) crear `pytest.ini` con `norecursedirs = data` y (B) añadir un archivo de ejemplo `tests/test_smoke.py` con el test home. Dime si quieres que haga eso ahora y lo implemento.
