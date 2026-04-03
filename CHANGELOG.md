# Changelog

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
