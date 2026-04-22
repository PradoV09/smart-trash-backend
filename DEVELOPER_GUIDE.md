# 🧠 Guía técnica interna del código

> **Proyecto:** `smart-trash-backend`
> **Autor:** `Heiner Jair Godoy Zamora y Jose Luis Prado Valencia`
> **Propósito:** un mapa de alto nivel para entender, mantener y escalar el backend.

---

## 1. Estructura de carpetas

- `main.py`: punto de entrada, routers, CORS, lifespan.
- `database.py`: motor async SQLAlchemy + Base + crear_tablas.
- `core/`: configuraciones, seguridad, dependencias, response builders, websocket management.
- `routers/`: endpoints por recurso + prefijos.
- `controllers/`: payloads FastAPI con dependencies y llamadas a servicios.
- `services/`: reglas de negocio, transacciones, validaciones fuertes.
- `models/`: ORM de tablas y relaciones.
- `schemas/`: contratos Pydantic de request/response.
- `alembic/`: migraciones de base de datos.

---

## 2. Flujo de desarrollo y debugging rápido

1. Cambia el modelo (`models/*`) y crea migración en Alembic.
2. Ajusta schema (`schemas/*`) y agrega `.as_form` si se envía formulario.
3. Implementa lógica en `services/*`.
4. Conecta la ruta en `controllers/*`.
5. Define el endpoint en `routers/*` con `response_model` y `status_code`.
6. Agrega/actualiza tests en `tests/test_api.py`.

---

## 3. Integración de seguridad y roles

- `core/security.py`: hash y verificación de contraseñas, creación y verificación JWT.
- `core/dependecies.py`: `get_current_user`, `require_rol` y tipos de dependencia.
- El rol se extrae del token y se compara con `TipoRol`.
- En `HTTPBearer` se usa `auto_error=False` para
  - capturar token ausente y lanzar `403` en vez de `401` por defecto,
  - manejar tokens inválidos/expirados como `401` mediante `verificar_token()`.

---

## 4. Optimizaciones y Correcciones Realizadas

### 4.1. Reorganización de `main.py`
- **Estructura modular:** Secciones claramente definidas con headers descriptivos
- **Lifespan functions:** `startup_handler` y `shutdown_handler` separados
- **Documentación completa:** Comentarios detallados y docstrings
- **Configuración FastAPI:** Metadata completa con contacto, licencia, etc.

### 4.2. Corrección de Errores de Sintaxis
- **Archivos de documentación:** Convertidos a comentarios puros (eliminado código ejecutable)
- **Archivos JavaScript:** Eliminado contenido HTML mezclado
- **Configuración de routers:** Eliminados prefijos duplicados
- **Variables de entorno:** JWT_SECRET generado correctamente

### 4.3. Optimización de WebSockets
- **Manejo robusto:** Mejor gestión de conexiones y desconexiones
- **Broadcast method:** Implementación mejorada en `websocket_manager.py`
- **Estadísticas:** Endpoint `/ws/stats` para monitoreo
- **Error handling:** Captura y manejo de excepciones

### 4.4. Configuración de Entorno
- **.env seguro:** JWT_SECRET generado con `secrets.token_hex(32)`
- **CORS múltiple:** Configurado para desarrollo y producción
- **Variables completas:** Todas las configuraciones necesarias incluidas

### 4.5. Archivos de Ejemplo y Testing
- **Ejemplos de integración:** Frontend y backend con código funcional
- **Pruebas de rendimiento:** Benchmarking con requests concurrentes
- **Tests de WebSockets:** Verificación completa de conexiones
- **Setup de pruebas:** Configuración automatizada

---

## 5. Mejores Prácticas Implementadas

### 5.1. Programación Asíncrona
- **Async/await completo:** Todas las operaciones I/O son asíncronas
- **SQLAlchemy async:** Consultas a BD no bloqueantes
- **HTTPx para APIs externas:** Llamadas HTTP asíncronas

### 5.2. Seguridad
- **JWT con expiración:** Tokens seguros con tiempo límite
- **RBAC completo:** 4 roles con permisos específicos
- **Hashing bcrypt:** Contraseñas seguras
- **Validación Pydantic:** Datos sanitizados

### 5.3. Testing
- **Cobertura completa:** 6 tests automatizados
- **Sintaxis verificada:** Todos los archivos compilables
- **Integración:** Tests de API y WebSockets

### 5.4. Documentación
- **README actualizado:** Información precisa del proyecto
- **CHANGELOG detallado:** Historial de cambios completo
- **Guías técnicas:** Documentación para desarrolladores
- **Ejemplos prácticos:** Código listo para usar

---

## 6. Generación de documentación para el equipo

- `API_DOCUMENTATION.md` cubre:
  - Resumen del sistema.
  - Arquitectura, reglas de negocio, endpoints y contratos.
- `DEVELOPER_GUIDE.md` cubre:
  - Estructura de proyecto y mejores prácticas.
  - Panorámica de archivos clave junto a ejemplos de mejora.
- `MANUAL_INTEGRACION_RUTAS.md` cubre:
  - Guía completa para integrar con API externa de rutas.
  - Configuración, ejemplos de código y testing.

---

## 5. Cómo contribuir rápido

1. Levanta con `uvicorn main:app --reload`.
2. Corre pruebas con `pytest -q`.
3. Usa Postman/Swagger (`/docs`) para iterar rutas.
4. Asegura la firma del token y los permisos de role-based access control (RBAC).

---

## 6. Mantenimiento de dependencias

Revisa `requirements.txt`. Mantén `FastAPI`, `SQLAlchemy`, `alembic`, `pydantic` y `passlib` actualizados.
