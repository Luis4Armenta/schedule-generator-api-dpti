# Diagrama de Flujo - Cache Granular por Período

## Flujo Principal

```
┌─────────────────────────────────────────┐
│  Request: POST /schedules/download      │
│  {                                      │
│    session_id: "xxx",                   │
│    career: "C",                         │
│    career_plan: "CI-2020",              │
│    plan_period: [4, 5, 7, 8],           │
│    force_full: false                    │
│  }                                      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Verificar autenticación                │
│  ¿session_id válido y no expirado?     │
└────────────────┬────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
      ❌ No           ✅ Sí
         │               │
         ▼               ▼
   HTTP 401      ┌─────────────────────────────┐
                 │  ¿force_full = true?         │
                 └──────────┬──────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                 ✅ Sí           ❌ No
                    │               │
                    │               ▼
                    │   ┌──────────────────────────────┐
                    │   │  check_missing_periods()      │
                    │   │  career="C", plan="CI-2020"   │
                    │   │  requested=[4,5,7,8]          │
                    │   └──────────┬───────────────────┘
                    │              │
                    │              ▼
                    │   ┌──────────────────────────────┐
                    │   │  Obtener períodos de DB:     │
                    │   │  {                            │
                    │   │    '4': timestamp_reciente,   │
                    │   │    '5': timestamp_reciente    │
                    │   │  }                            │
                    │   └──────────┬───────────────────┘
                    │              │
                    │              ▼
                    │   ┌──────────────────────────────┐
                    │   │  Calcular missing_periods:   │
                    │   │  • [7,8] no existen en DB    │
                    │   │  • [4,5] timestamp < 7 días  │
                    │   │  → missing_periods = [7, 8]  │
                    │   └──────────┬───────────────────┘
                    │              │
                    └──────────────┤
                                   │
                 missing_periods = [4,5,7,8] (force_full)
                 o missing_periods = [7,8] (auto)
                                   │
                         ┌─────────┴─────────┐
                         │                   │
              len(missing) > 0     len(missing) = 0
                         │                   │
                         ▼                   ▼
        ┌────────────────────────┐  ┌────────────────────────┐
        │  DESCARGA COMPLETA      │  │  SOLO DISPONIBILIDAD   │
        └────────────────────────┘  └────────────────────────┘
```

## Ruta 1: Descarga Completa (missing_periods > 0)

```
┌──────────────────────────────────────────┐
│  scraper.download_schedules()            │
│  plan_periods = missing_periods [7, 8]   │
│  ↓ Selenium navega SAES                  │
│  ↓ Parsea tablas de horarios             │
│  ↓ Extrae: sequence, subject, teacher,   │
│            schedule, credits, etc.       │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  scraper.download_availability()         │
│  ↓ Selenium navega disponibilidad        │
│  ↓ Parsea tabla de ocupación             │
│  ↓ Extrae: sequence, subject,            │
│            course_availability           │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  Combinar datos:                         │
│  for course in courses:                  │
│    key = (sequence, subject)             │
│    course.availability =                 │
│      availability_map[key]               │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  course_service.upload_courses()         │
│  ↓ Itera cada curso                      │
│  ↓ upsert_course(course)                 │
│    → MongoDB.update_one(                 │
│        {sequence, subject},              │
│        {$set: course_data},              │
│        upsert=True                       │
│      )                                   │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  set_downloaded_periods()                │
│  career="C", plan="CI-2020"              │
│  periods=[7, 8], timestamp=now           │
│  ↓ MongoDB.update_one(                   │
│      {career, plan},                     │
│      {$set: {                            │
│        'periods.7': now,                 │
│        'periods.8': now                  │
│      }},                                 │
│      upsert=True                         │
│    )                                     │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  Response:                               │
│  {                                       │
│    status: "success",                    │
│    message: "Descarga completa: 85       │
│              cursos guardados en DB",    │
│    courses: [...],                       │
│    total_courses: 85                     │
│  }                                       │
└──────────────────────────────────────────┘
```

## Ruta 2: Solo Disponibilidad (missing_periods = 0)

```
┌──────────────────────────────────────────┐
│  Todos los períodos solicitados ya       │
│  están en DB y actualizados (<7 días)    │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  scraper.download_availability()         │
│  ↓ Selenium navega solo disponibilidad   │
│  ↓ Parsea tabla de ocupación             │
│  ↓ Extrae: sequence, subject,            │
│            course_availability           │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  Actualizar solo disponibilidad:         │
│  for item in availability_data:          │
│    update_course_availability(           │
│      sequence=item['sequence'],          │
│      subject=item['subject'],            │
│      availability=item['availability']   │
│    )                                     │
│    ↓ MongoDB.update_one(                 │
│        {sequence, subject},              │
│        {$set: {                          │
│          course_availability: X          │
│        }}                                │
│      )                                   │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  Obtener cursos de MongoDB:              │
│  get_courses(                            │
│    career="C",                           │
│    levels=[1..9],                        │
│    semesters=[1..12],                    │
│    shifts=['M','V']                      │
│  )                                       │
│  ↓ Filtrar por plan="CI-2020"           │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│  Response:                               │
│  {                                       │
│    status: "success",                    │
│    message: "Actualización de            │
│              disponibilidad: 118         │
│              cursos actualizados",       │
│    courses: [...],                       │
│    total_courses: 220                    │
│  }                                       │
└──────────────────────────────────────────┘
```

## Lógica de check_missing_periods()

```
check_missing_periods(career, plan, requested_periods)
    │
    ▼
┌─────────────────────────────────────────┐
│  Obtener períodos descargados:          │
│  downloaded = get_downloaded_periods()  │
│  → {                                    │
│      '4': 1700000000.0,                 │
│      '5': 1700000000.0,                 │
│      '7': 1704200000.0                  │
│    }                                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  current_time = time.time()             │
│  week_in_seconds = 7 * 24 * 60 * 60    │
│  missing = []                           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Para cada período solicitado:          │
│  for period in [4, 5, 7, 8]:            │
└────────────────┬────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
  period='4'            period='8'
      │                     │
      ▼                     ▼
  '4' in downloaded?    '8' in downloaded?
      │                     │
   ✅ Sí                  ❌ No
      │                     │
      ▼                     ▼
  timestamp = 1700000000   missing.append(8)
  age = current - ts
      │
  age > week? ✅ Sí
      │
      ▼
  missing.append(4)

                 │
                 ▼
┌─────────────────────────────────────────┐
│  Resultado:                             │
│  missing = [4, 8]                       │
│  (4 está desactualizado, 8 no existe)   │
└─────────────────────────────────────────┘
```

## Ejemplo Completo: Escenario Real

### Estado Inicial (DB)
```
course_metadata: {
  career: 'C',
  plan: 'CI-2020',
  periods: {
    '7': 1732100000.0,  // Descargado hace 3 días
    '8': 1732100000.0   // Descargado hace 3 días
  }
}

courses: [
  {sequence: '7CM70', subject: 'Redes', ...},
  {sequence: '7CM71', subject: 'SO', ...},
  {sequence: '8CM80', subject: 'Compiladores', ...},
  ...
] (Total: 135 cursos de períodos 7 y 8)
```

### Request
```json
{
  "session_id": "xyz123",
  "career": "C",
  "career_plan": "CI-2020",
  "plan_period": [4, 5, 7, 8],
  "force_full": false
}
```

### Procesamiento
```
1. check_missing_periods("C", "CI-2020", [4,5,7,8])
   → downloaded = {'7': timestamp_3días, '8': timestamp_3días}
   → [4] no existe → missing
   → [5] no existe → missing
   → [7] existe, <7 días → OK
   → [8] existe, <7 días → OK
   → missing_periods = [4, 5]

2. needs_full_download = len([4,5]) > 0 → TRUE

3. Descarga completa de períodos [4, 5]
   → scraper.download_schedules(plan_periods=[4,5])
   → Descarga 85 cursos de períodos 4 y 5

4. scraper.download_availability()
   → Descarga disponibilidad de TODOS [4,5,7,8]
   → 220 registros de disponibilidad

5. Combinar + guardar solo los [4,5] descargados
   → upload_courses(85 cursos) → upsert en MongoDB

6. set_downloaded_periods([4,5], timestamp_now)
   → Actualiza metadata: {'4': now, '5': now, '7': old, '8': old}

7. Response:
   {
     status: "success",
     message: "Descarga completa: 85 cursos guardados en DB",
     courses: [... 85 cursos ...],
     total_courses: 85
   }
```

### Estado Final (DB)
```
course_metadata: {
  career: 'C',
  plan: 'CI-2020',
  periods: {
    '4': 1732360000.0,  // NUEVO
    '5': 1732360000.0,  // NUEVO
    '7': 1732100000.0,  // Sin cambios
    '8': 1732100000.0   // Sin cambios
  }
}

courses: [
  ... 85 cursos NUEVOS de períodos 4 y 5 ...,
  ... 135 cursos EXISTENTES de períodos 7 y 8 (disponibilidad actualizada) ...
] (Total: 220 cursos)
```
