# Plan de Pruebas (Versión Académica)

Proyecto: Schedule-Generator-API

Autor: Equipo de proyecto

Fecha: 30/11/2025

Versión: 1.0

Resumen ejecutivo
------------------
Este documento describe el plan de pruebas formal del backend "Schedule-Generator-API" diseñado para validar la corrección funcional, la robustez frente a errores comunes y la capacidad de integración con adaptadores externos (p. ej. repositorio MongoDB y scraper SAES). El plan está pensado para ser reproducible durante la entrega académica y proporciona criterios de aceptación cuantificables.

1. Objetivos de las pruebas
--------------------------
- Verificar que las funcionalidades principales del backend cumplan los requisitos funcionales especificados: generación de horarios, descarga de horarios desde SAES y manejo de sesiones/captcha.
- Encontrar defectos de severidad alta y media que impidan la demostración o el uso básico del servicio.
- Proveer evidencia reproducible (registros y resultados de pytest) que respalden la entrega académica.

2. Alcance
---------
Incluye:
- Pruebas unitarias sobre servicios de dominio y componentes lógicos (ScheduleService, CourseService).
- Pruebas de integración simulada para endpoints críticos (`/schedules/`, `/schedules/download`) mediante mocks/stubs de adaptadores externos (SAESScraperService, MongoCourseRepository).
- Pruebas de humo sobre la API REST (ruta raíz y endpoints documentados).

Excluye:
- Pruebas E2E reales con Selenium contra SAES en producción (salvo que el entorno esté totalmente preparado y autorizado).
- Pruebas de carga y rendimiento.

3. Estrategia de pruebas
-----------------------
Se emplea una estrategia escalonada:

- Nivel Unitario: pruebas aisladas por función/clase usando mocks para dependencias externas.
- Nivel de Integración (simulada): invocación de endpoints con `TestClient` de FastAPI y sustitución (monkeypatch) de adaptadores externos por stubs controlados.
- Smoke/System Sanity: comprobación de endpoints clave mediante tests rápidos que demuestren disponibilidad y respuesta adecuada.

4. Criterios de entrada y salida
--------------------------------
Entrada (para iniciar la campaña de pruebas):
- Repositorio clonado y dependencias instaladas (virtualenv activo y `pip install -r requirements.txt`).
- Configuración local: `.env` con variables mínimas si fuese necesario (no necesario para pruebas con mocks).

Salida (criterios para considerar la campaña satisfactoria):
- Todos los tests P0 pasan: smoke + 1 test unitario de ScheduleService + 1 test de integración simulada para `/schedules/download`.
- No existen errores de recolección en pytest (p. ej. por directorios no accesibles).

5. Plan de casos de prueba (seleccionados)
-----------------------------------------
Cada caso incluye: identificador, objetivo, precondición, pasos, datos de prueba, resultado esperado.

TC-P0-01: Smoke — Ruta raíz
- Objetivo: verificar disponibilidad básica del servicio.
- Precondición: app importable.
- Pasos: GET `/` vía TestClient.
- Datos: ninguno.
- Esperado: HTTP 200 y cuerpo contiene "Profesores API".

TC-P0-02: Unit — ScheduleService (happy path)
- Objetivo: validar que el generador produce un conjunto de horarios sin excepciones.
- Precondición: stub de CourseService que devuelve 5 cursos válidos.
- Pasos: llamar `generate_schedules` con parámetros simples.
- Datos: levels=['1'], career='A', length=3, start_time='08:00', end_time='14:00'.
- Esperado: lista de horarios con tamaño <= 3 y sin excepciones.

TC-P0-03: Integration-simulado — download_schedules_endpoint (sesión inválida)
- Objetivo: validar manejo de sesiones ausentes/expiradas.
- Precondición: `login_store` no contiene la sesión suministrada.
- Pasos: POST `/schedules/download` con `session_id: 'fake'`.
- Datos: JSON con session_id fake.
- Esperado: HTTP 401 y mensaje de error de sesión.

TC-P0-04: Integration-simulado — download_schedules_endpoint (happy path con stub)
- Objetivo: demostrar flujo de descarga sin Selenium ni Mongo reales.
- Precondición: inyectar `login_store` con cookies válidas y monkeypatch de `SAESScraperService` que retorne 2 cursos y disponibilidades.
- Pasos: POST `/schedules/download` con body válido.
- Datos: session_id='test-session', career='A', career_plan='05', plan_period=['1'].
- Esperado: HTTP 200, `status: "success"`, `total_courses==2`.

6. Matriz de trazabilidad (sugerida)
----------------------------------
Crear una tabla que relacione requisitos (IDs) con casos de prueba y tests automatizados. Por ejemplo:

| Requisito | Caso de prueba | Test automático |
|-----------|----------------|-----------------|
| GEN-001   | TC-P0-02       | tests/schedules/test_schedule_service.py::TestScheduleService::test_correct_len_of_courses_per_schedule |

7. Evidencia y artefactos
-------------------------
- `tests/results.txt` — salida completa de pytest.
- `reports/junit.xml` — formato JUnit (recomendado para CI / entrega formal).
- `reports/coverage_html/` — reporte de cobertura HTML (opcional).
- `scripts/run_tests.sh` — script reproducible para ejecutar los tests.

8. Criterios de aceptación académicos
-----------------------------------
- Documentación del plan (entregado: `TEST_PLAN_ACADEMIC.md` y `TEST_PLAN.md`).
- Pruebas automatizadas ejecutadas con resultados adjuntos (`tests/results.txt`).
- Al menos 80% de los tests P0/P1 verdes para considerar la entrega con éxito (en este caso, objetivo 100% para demo).

9. Anexos: comandos reproducibles
--------------------------------
```bash
# Activar entorno
source .venv/bin/activate

# Ejecutar tests y generar JUnit
.venv/bin/python -m pytest -v --junitxml=reports/junit.xml | tee tests/results.txt

# (Opcional) generar coverage
pip install pytest-cov
.venv/bin/python -m pytest --cov=. --cov-report=html:reports/coverage_html
```

10. Observaciones finales
------------------------
Para la entrega académica se priorizó la reproducibilidad y la evidencia (tests, scripts y resultados). Se documentó tanto un plan práctico para la demo como una versión académica formal con criterios y trazabilidad sugerida.
