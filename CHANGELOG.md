# Changelog

## [1.0.3] - 2026-04-15

### Added
- **Módulo de Tripulación Asignada** - Nuevo módulo completo:
  - `controller_asignaciontripulacion.py` - Controladores para gestión de tripulación
  - `router_asignaciontripulacion.py` - Routers separados por roles (admin, driver, recolector)
  - `service_asignaciontripulacion.py` - Servicios de lógica de negocio
  - `model_asignaciontripulacion.py` - Modelo ORM `TripulacionAsignacion`
  - `schema_asignaciontripulacion.py` - Schemas Pydantic para validación

### Security
- **Restricción de roles para Admin:**
  - Admin solo puede crear usuarios con roles: `admin`, `driver`, `recolector`
  - Validación implementada en `service_usuarios.py` (`crear_por_admin` y `actualizar_usuario`)
  - Error HTTP 403 si se intenta asignar rol `user` desde administración
- **Usuarios públicos sin acceso de autenticación:**
  - Usuarios con rol `user` no pueden iniciar sesión (HTTP 403 Forbidden)
  - Validación en `service_auth.py` en método `login`
- **Registro público eliminado del MVP:**
  - Endpoint `POST /auth/registro` eliminado
  - Solo el admin puede crear usuarios en el sistema
  - Rol `user` ya no se utiliza en el MVP

### Fixed
- **Corrección de importaciones rotas en módulo de tripulación:**
  - `schema_asignacionrutas.py`: import corregido de `schema_asignaciontripulacion`
  - `service_asignacionrutas.py`: import del modelo y `selectinload` corregidos
  - `controller_asignacionrutas.py`: imports de `schema_asignaciontripulacion` y `service_asignaciontripulacion`
  - `service_asignaciontripulacion.py`: agregado import del modelo `TripulacionAsignacion`
- **Renombrado de archivos con espacios en nombres:**
  - `model_asignaciontripulacion .py` → `model_asignaciontripulacion.py`
  - `service_asignaciontripulacion .py` → `service_asignaciontripulacion.py`
  - `schema_asignaciontripulacion .py` → `schema_asignaciontripulacion.py`

### Changed
- **main.py actualizado:**
  - Agregados imports de routers de tripulación (sin recolector)
  - Montados routers de tripulación en la app FastAPI
  - Eliminados tags duplicados que causaban grupos repetidos en Swagger UI
- **service_asignaciontripulacion.py:**
  - Agregados métodos `obtener_tripulacion_asignacion()` y `obtener_miembro_tripulacion()`
- **MVP simplificado - Roles y funcionalidades:**
  - **Admin**: Crea usuarios (admin/driver/recolector), gestiona asignaciones y tripulación
  - **Driver**: Confirma participación, inicia/finaliza recorridos, consulta asignación y tripulación
  - **Recolector**: Rol pasivo - solo existe como entidad para ser asignado a tripulación (sin endpoints)
  - **User**: Eliminado del MVP - no hay registro público

### Removed
- **Endpoints de recolector eliminados:**
  - `router_recolector` de `router_asignacionrutas.py`
  - `router_recolector` de `router_asignaciontripulacion.py`
  - Controllers `ver_asignacion_recolector` y `confirmar_participacion` del recolector
- **Registro público eliminado:**
  - `POST /auth/registro` endpoint
  - `registro_publico` controller y service
  - Tests relacionados con registro público
- **Endpoints duplicados eliminados de `router_asignacionrutas.py`:**
  - `POST /{id}/tripulacion` (ya existe en `router_asignaciontripulacion.py`)
  - `DELETE /{id}/tripulacion/{id_usuario}` (ya existe en `router_asignaciontripulacion.py`)

### Tests
- `pytest -q` pasa: `8 passed` (anteriormente 10, se eliminaron 2 tests de registro público).
- Todos los tests de autenticación y autorización funcionando correctamente.
- Validaciones de seguridad probadas y verificadas.

---

## [1.0.2] - 2026-04-02

### Added
- Integración con API externa de rutas:
  - Servicio `service_rutas_externo.py` para llamadas HTTP a API de rutas
  - Validación automática de rutas al crear asignaciones
  - Endpoint `/admin/asignaciones/rutas/{id_ruta}` para consultar detalles de rutas externas
  - Configuración `RUTAS_API_URL` en settings
- Dependencia `httpx` para llamadas HTTP asíncronas
- Endpoint `/health` para monitoreo de salud de la API
- WebSockets con endpoint `/ws/stats` para estadísticas de conexiones

### Fixed
- Ajustada la seguridad en `core/dependecies.py`:
  - `HTTPBearer(auto_error=False)` para manejo manual de token.
  - token ausente -> 403, token inválido/expirado -> 401.
- Corrección en `controller_vehiculo.py`:
  - Todos los endpoints retornan `SuccessResponse[...]` (incluye delete con `dict[str,int]`).
- `controller_auth.py` + `schema_auth.py`:
  - login ahora usa `LoginRequest.as_form()` y el controller retorna `SuccessResponse[TokenResponse]`.
- `routers` y `schemas` actualizados para consistencia de `response_model`.
- **Corrección de errores de sintaxis en archivos creados:**
  - `configuracion-integracion.py`: Convertido a documentación pura (eliminado código ejecutable mezclado)
  - `ejemplo-frontend.js`: Eliminado contenido HTML mezclado
  - `main.py`: Corregida indentación incorrecta
- **Configuración de routers:** Eliminados prefijos duplicados en `main.py`
- **Variables de entorno:** JWT_SECRET generado correctamente y RUTAS_API_URL agregado

### Changed
- **Reorganización completa de `main.py`:**
  - Estructura modular con secciones claras
  - Documentación completa y comentarios descriptivos
  - Lifespan functions separadas y bien documentadas
  - Configuración FastAPI mejorada con metadata completa
- **Optimización de WebSockets:**
  - Mejor manejo de conexiones y desconexiones
  - Método `broadcast` mejorado en `websocket_manager.py`
  - Estadísticas de conexiones disponibles
- **Configuración .env segura:**
  - JWT_SECRET generado con `secrets.token_hex(32)`
  - CORS_ORIGINS actualizado con múltiples orígenes
  - Variables de entorno completas y documentadas

### Added
- Documentación actualizada en `DEVELOPER_GUIDE.md` y `API_DOCUMENTATION.md` con detalle de la seguridad JWT/RBAC.
- Se agregó sección de evaluación de calidad y puntuación de la API en `API_DOCUMENTATION.md`.
- **Archivos de ejemplo creados:**
  - `ejemplo-frontend.js`: Integración JavaScript con la API
  - `ejemplo-backend.py`: Integración Python con APIs externas
  - `benchmark_performance.py`: Pruebas de rendimiento
  - `test_websockets.py`: Pruebas de WebSockets
  - `setup_websocket_test.py`: Configuración de pruebas
- **README.md completamente actualizado:**
  - Información precisa sobre el estado actual del proyecto
  - Instrucciones de instalación detalladas
  - Sección de optimizaciones y correcciones realizadas
  - Estado de tests y funcionalidades implementadas

### Tests
- `pytest -q` pasa: `6 passed`.
- Tests de WebSockets implementados y funcionales.
- Verificación de sintaxis en todos los archivos creados.

## [1.0.1] - 2026-04-02

### Fixed
- Ajustada la seguridad en `core/dependecies.py`:
  - `HTTPBearer(auto_error=False)` para manejo manual de token.
  - token ausente -> 403, token inválido/expirado -> 401.
- Corrección en `controller_vehiculo.py`:
  - Todos los endpoints retornan `SuccessResponse[...]` (incluye delete con `dict[str,int]`).
- `controller_auth.py` + `schema_auth.py`:
  - login ahora usa `LoginRequest.as_form()` y el controller retorna `SuccessResponse[TokenResponse]`.
- `routers` y `schemas` actualizados para consistencia de `response_model`.

### Added
- Documentación actualizada en `DEVELOPER_GUIDE.md` y `API_DOCUMENTATION.md` con detalle de la seguridad JWT/RBAC.
- Se agregó sección de evaluación de calidad y puntuación de la API en `API_DOCUMENTATION.md`.

### Tests
- `pytest -q` pasa: `6 passed`.
