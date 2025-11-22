# Documentación Técnica - Schedule Generator API

Esta carpeta contiene toda la documentación técnica del proyecto organizada por categorías.

## 📖 Índice

### 🏗️ Arquitectura

#### [HEXAGONAL_ARCHITECTURE.md](HEXAGONAL_ARCHITECTURE.md)
Explicación completa del patrón de Arquitectura Hexagonal (Puertos y Adaptadores) implementado en el proyecto.

**Contenido:**
- Estructura por módulos (courses, schedules, routes)
- Capa de Dominio: Entidades y Puertos
- Capa de Aplicación: Servicios y Casos de Uso
- Capa de Infraestructura: Adaptadores
- Inyección de Dependencias
- Beneficios y principios aplicados

#### [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)
Diagramas visuales ASCII completos del sistema con flujos de datos.

**Contenido:**
- Vista general del sistema
- Flujo completo de una request (POST /schedules/download)
- Diagramas de capas y responsabilidades
- Reglas de dependencia
- Ejemplos de código correcto vs violaciones
- Puntos de extensión

### 💾 Persistencia

#### [MONGODB_PERSISTENCE.md](MONGODB_PERSISTENCE.md)
Estrategia de persistencia con cache granular por período.

**Contenido:**
- Contexto en arquitectura hexagonal
- Comportamiento del cache (primera descarga, actualizaciones)
- Estructura de datos en MongoDB
- Métodos del repositorio (upsert, update_availability, check_missing_periods)
- Escenarios de uso real
- Ventajas del diseño

### 🔄 Flujos

#### [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md)
Diagramas de flujo detallados del sistema de descarga de horarios.

**Contenido:**
- Flujo principal de descarga
- Ruta 1: Descarga completa (períodos faltantes)
- Ruta 2: Solo disponibilidad (cache vigente)
- Lógica de check_missing_periods()
- Ejemplo completo con estado inicial y final de DB

### 🔐 Integración

#### [CAPTCHA_USAGE.md](CAPTCHA_USAGE.md)
Documentación sobre el manejo de autenticación con SAES.

**Contenido:**
- Flujo de login con CAPTCHA
- Manejo de sesiones
- Endpoints de autenticación
- Troubleshooting

### 📝 Historial

#### [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
Resumen de cambios y decisiones técnicas implementadas.

**Contenido:**
- Cambios en scraper (Selenium + geckodriver)
- Implementación de cache granular
- Mejoras en logging
- Solución de errores de validación

## 🚀 Guía de Lectura Recomendada

### Para entender la arquitectura:
1. Empezar con [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) para vista general visual
2. Profundizar en [HEXAGONAL_ARCHITECTURE.md](HEXAGONAL_ARCHITECTURE.md) para conceptos
3. Ver [MONGODB_PERSISTENCE.md](MONGODB_PERSISTENCE.md) como ejemplo de adaptador

### Para implementar features nuevas:
1. Revisar [HEXAGONAL_ARCHITECTURE.md](HEXAGONAL_ARCHITECTURE.md) - Sección "Próximos Pasos"
2. Ver [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) - Sección "Puntos de Extensión"
3. Seguir el patrón de puertos y adaptadores existente

### Para debugging:
1. Revisar [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md) para entender flujo completo
2. Consultar [MONGODB_PERSISTENCE.md](MONGODB_PERSISTENCE.md) para cache
3. Ver [CAPTCHA_USAGE.md](CAPTCHA_USAGE.md) para problemas de autenticación

## 🔗 Enlaces Rápidos

- [README principal](../README.md)
- [Código fuente](../)
- [Requirements](../requirements.txt)
- [Docker Compose](../docker-compose.yml)

## 📌 Convenciones

- **Puerto**: Interfaz (clase abstracta) en `domain/ports/`
- **Adaptador**: Implementación concreta en `infrastructure/`
- **Servicio**: Lógica de aplicación en `application/`
- **Entidad**: Modelo de dominio en `domain/model/`

## 🤝 Contribuciones

Al agregar nueva documentación:
1. Crear el archivo `.md` en esta carpeta
2. Agregarlo a este índice con descripción
3. Actualizar enlaces en README principal si es necesario
4. Seguir el formato de secciones con emojis
