# Estrategia de Persistencia MongoDB

## Resumen
Se implementó un sistema de persistencia en MongoDB con **cache granular por período** para optimizar las descargas desde SAES. Cada período (semestre) se rastrea individualmente con su timestamp.

## Comportamiento

### Primera descarga (base de datos vacía)
- Se realiza **descarga completa** de horarios + disponibilidad para los períodos solicitados
- Todos los cursos se guardan en MongoDB usando upsert (sequence + subject como clave única)
- Se registra timestamp **por cada período descargado** en colección `course_metadata`

### Descargas posteriores - Escenarios

#### Caso 1: Todos los períodos ya descargados + actualizados (<7 días)
**Ejemplo**: Ya se descargaron períodos [7, 8] hace 3 días, se solicitan [7, 8]
- **Solo se descarga disponibilidad** desde SAES
- Se actualizan únicamente los campos `course_availability` en MongoDB
- **Beneficio**: ~90% más rápido (evita parsear todas las tablas de horarios)

#### Caso 2: Algunos períodos faltantes o desactualizados
**Ejemplo**: Ya se descargaron períodos [7, 8] hace 3 días, se solicitan [4, 5, 7, 8]
- Se detecta que [4, 5] **nunca fueron descargados** → missing_periods = [4, 5]
- Se realiza **descarga completa solo de períodos [4, 5]**
- Se hace upsert de cursos nuevos en MongoDB
- Se registran timestamps de períodos [4, 5]
- Luego se actualiza disponibilidad de **todos** los períodos [4, 5, 7, 8]

#### Caso 3: Períodos desactualizados (≥7 días)
**Ejemplo**: Ya se descargaron períodos [7, 8] hace 10 días, se solicitan [7, 8]
- Se detecta que [7, 8] están **desactualizados** → missing_periods = [7, 8]
- Se realiza **descarga completa de [7, 8]**
- Se actualizan horarios, profesores, etc. en MongoDB
- Se actualizan timestamps de [7, 8]

### Forzar descarga completa
- Usar `force_full: true` en el request
- **Ignora timestamps** y descarga todos los períodos solicitados
- Útil para:
  - Inicios de semestre
  - Cambios administrativos
  - Debugging

## Estructura de datos

### Colección `courses`
```python
{
  'sequence': '4CM40',         # Clave única (junto con subject)
  'subject': 'Bases de Datos', # Clave única (junto con sequence)
  'semester': '4',
  'career': 'C',
  'level': '4',
  'plan': 'CI-2020',
  'shift': 'M',
  'teacher': 'García López Juan',
  'schedule': 'L-V: 07:00-09:00',
  'course_availability': 15,    # Campo que se actualiza frecuentemente
  'required_credits': 8.5,
  'teacher_positive_score': 4.2
}
```

### Colección `course_metadata` (MODIFICADA)
```python
{
  'career': 'C',
  'plan': 'CI-2020',
  'periods': {
    '4': 1704225600.0,  # Unix timestamp de descarga del período 4
    '5': 1704225600.0,  # Unix timestamp de descarga del período 5
    '7': 1704139200.0,  # Unix timestamp de descarga del período 7
    '8': 1704139200.0   # Unix timestamp de descarga del período 8
  }
}
```

## Métodos implementados

### MongoCourseRepository

#### `upsert_course(course: Course) -> bool`
- Inserta o actualiza un curso usando `sequence + subject` como clave única
- Retorna `True` si la operación fue exitosa

#### `insert_courses(courses: List[Course]) -> int`
- Inserta múltiples cursos usando upsert
- Retorna el número de cursos guardados exitosamente

#### `update_course_availability(sequence: str, subject: str, availability: int) -> bool`
- Actualiza **solo** el campo `course_availability` de un curso existente
- Operación atómica y rápida
- Retorna `True` si se modificó algún registro

#### `get_downloaded_periods(career: str, plan: str) -> dict` (NUEVO)
- Obtiene el diccionario de períodos descargados con sus timestamps
- Retorna `{}` si nunca se ha descargado nada
- Ejemplo: `{'4': 1704225600.0, '5': 1704225600.0}`

#### `set_downloaded_periods(career: str, plan: str, periods: List[int], timestamp: float) -> None` (NUEVO)
- Registra los períodos descargados con su timestamp
- **Actualiza solo los períodos especificados**, preserva los existentes
- Usa upsert para crear o actualizar el metadato

#### `check_missing_periods(career: str, plan: str, requested_periods: List[int]) -> List[int]` (NUEVO)
- Verifica qué períodos solicitados **NO están descargados o están desactualizados (>7 días)**
- Retorna lista de períodos que necesitan descarga completa
- Ejemplo: `requested=[4,5,7,8]`, `downloaded={7:timestamp_reciente, 8:timestamp_reciente}` → retorna `[4, 5]`

### CourseService

#### `upload_courses(courses: List[Course]) -> int`
- Wrapper para guardar cursos en MongoDB
- Retorna el número de cursos guardados

#### `update_availability(sequence: str, subject: str, availability: int) -> bool`
- Wrapper para actualizar solo disponibilidad
- Retorna `True` si se actualizó

#### `get_downloaded_periods(career: str, plan: str) -> dict` (NUEVO)
- Wrapper para obtener períodos descargados con timestamps

#### `set_downloaded_periods(career: str, plan: str, periods: List[int], timestamp: float) -> None` (NUEVO)
- Wrapper para registrar períodos descargados

#### `check_missing_periods(career: str, plan: str, requested_periods: List[int]) -> List[int]` (NUEVO)
- Wrapper para verificar períodos faltantes o desactualizados

## Endpoint `/schedules/download`

### Request
```json
{
  "session_id": "ae3f8c1b2d",
  "career": "C",
  "career_plan": "CI-2020",
  "plan_period": [4],
  "shift": "M",
  "force_full": false  // Opcional, default: false
}
```

### Response (descarga completa)
```json
{
  "status": "success",
  "message": "Descarga completa: 120 cursos guardados en DB",
  "courses": [...],
  "total_courses": 120
}
```

### Response (solo disponibilidad)
```json
{
  "status": "success",
  "message": "Actualización de disponibilidad: 118 cursos actualizados",
  "courses": [...],
  "total_courses": 120
}
```

## Ventajas

1. **Performance**: Actualizar solo disponibilidad es ~10x más rápido
2. **Granularidad**: Cada período se rastrea independientemente
3. **Eficiencia**: Solo descarga períodos faltantes o desactualizados
4. **Consistencia**: Upsert garantiza que no haya duplicados
5. **Flexibilidad**: `force_full` permite forzar refresh cuando sea necesario
6. **Escalabilidad**: MongoDB maneja eficientemente las actualizaciones parciales
7. **Auditoría**: Los timestamps por período permiten rastrear cuándo se actualizó cada uno

## Escenarios de uso real

### Escenario 1: Usuario nuevo descarga semestre 4 y 5
```
Request: {periods: [4, 5]}
Estado DB: vacío
Resultado: Descarga completa de [4, 5] → guarda en DB con timestamps
```

### Escenario 2: Mismo usuario recarga después de 2 días
```
Request: {periods: [4, 5]}
Estado DB: {4: timestamp_reciente, 5: timestamp_reciente}
Resultado: Solo actualiza disponibilidad (sin descargar horarios)
```

### Escenario 3: Usuario solicita períodos adicionales
```
Request: {periods: [4, 5, 7, 8]}
Estado DB: {4: timestamp_reciente, 5: timestamp_reciente}
missing_periods: [7, 8]
Resultado: 
  1. Descarga completa solo de [7, 8]
  2. Guarda [7, 8] en DB
  3. Actualiza disponibilidad de todos [4, 5, 7, 8]
```

### Escenario 4: Nuevo semestre (períodos desactualizados)
```
Request: {periods: [4, 5]}
Estado DB: {4: timestamp_antiguo (>7 días), 5: timestamp_antiguo (>7 días)}
missing_periods: [4, 5]
Resultado: Descarga completa de [4, 5] → actualiza DB con nuevos timestamps
```

## Consideraciones

- **Cache de 7 días**: Ajustar según frecuencia de cambios en SAES
- **Índices MongoDB**: Agregar índice compuesto `{sequence: 1, subject: 1}` para queries rápidas
- **Índice adicional**: `{career: 1, plan: 1, semester: 1}` para filtrado por período
- **Limpieza**: Considerar eliminar cursos obsoletos de semestres muy antiguos
- **Concurrencia**: Implementar locks si múltiples usuarios pueden descargar simultáneamente
- **Validación**: Verificar que períodos solicitados existan en SAES (1-10 típicamente)

## Testing

```bash
# Escenario 1: Primera descarga (períodos 4 y 5)
curl -X POST http://localhost:8000/schedules/download \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "career": "C", "career_plan": "CI-2020", "plan_period": [4, 5]}'
# → Descarga completa de [4, 5]

# Escenario 2: Segunda descarga < 7 días (mismos períodos)
curl -X POST http://localhost:8000/schedules/download \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "career": "C", "career_plan": "CI-2020", "plan_period": [4, 5]}'
# → Solo actualiza disponibilidad

# Escenario 3: Agregar períodos nuevos (7 y 8)
curl -X POST http://localhost:8000/schedules/download \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "career": "C", "career_plan": "CI-2020", "plan_period": [4, 5, 7, 8]}'
# → Descarga completa solo de [7, 8], actualiza disponibilidad de todos

# Escenario 4: Forzar descarga completa de todos
curl -X POST http://localhost:8000/schedules/download \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "career": "C", "career_plan": "CI-2020", "plan_period": [4, 5], "force_full": true}'
# → Descarga completa de [4, 5] ignorando cache
```

## Logs

### Descarga completa de períodos faltantes
```
[Endpoint] Períodos solicitados: [4, 5, 7, 8]
[Endpoint] Períodos que necesitan descarga: [7, 8]
[Endpoint] Descarga completa de períodos: [7, 8]
[Endpoint] Cursos descargados=85
[Endpoint] Disponibilidades descargadas=220
[Endpoint] Guardados 85 cursos en MongoDB
```

### Solo actualización de disponibilidad
```
[Endpoint] Períodos solicitados: [4, 5]
[Endpoint] Períodos que necesitan descarga: []
[Endpoint] Todos los períodos [4, 5] ya están descargados y actualizados
[Endpoint] Solo actualización de disponibilidad
[Endpoint] Disponibilidades descargadas=120
[Endpoint] Actualizada disponibilidad de 118 cursos
```

### Forzar descarga completa
```
[Endpoint] force_full=True, descargando todos los períodos: [4, 5, 7, 8]
[Endpoint] Descarga completa de períodos: [4, 5, 7, 8]
[Endpoint] Cursos descargados=220
[Endpoint] Guardados 220 cursos en MongoDB
```
