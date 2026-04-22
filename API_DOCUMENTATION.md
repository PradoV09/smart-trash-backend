# 📘 Documentación técnica y funcional de la API

> **Proyecto:** `smart-trash-backend`
> **Framework:** FastAPI
> **Versión:** `1.0.2`
> **Autor:** `Heiner Jair Godoy Zamora y Jose Luis Prado Valencia`
> **Fecha de revisión:** `2 de abril de 2026`

---

## 1. Resumen ejecutivo

Smart Trash Route es un backend FastAPI para la gestión de rutas de recolección de desechos, que soporta:

- Autenticación JWT y autorización por roles (RBAC).
- CRUD de usuarios y vehículos (módulo admin).
- Administración de reportes operativos.
- Asignación de rutas/vehículos y logica de tripulación.
- Sesiones de WebSocket para eventos en tiempo real de cada asignación.
- **Integración con APIs externas** para validación de rutas.
- **Optimización completa** con async/await y manejo robusto de errores.

---

## 2. Arquitectura y flujo general

- Capas: routers → controllers → services → models + DB → schemas.
- Core: seguridad, dependencias, respuestas uniformes y WebSocket manager.
- **Optimización:** Programación asíncrona completa, cache para APIs externas.

### 2.1. Flujo de una petición HTTP

1. Cliente envía request a un endpoint.
2. Router decide el path y aplica `Depends` (autorización, body parsing).
3. Controller valida contexto y delega al Service.
4. Service ejecuta reglas de negocio con SQLAlchemy asíncrono (`AsyncSession`).
5. Controller retorna usando `success_response` y el esquema Pydantic.

### 2.2. Optimizaciones Implementadas

- **Async/Await completo:** Todas las operaciones I/O son no bloqueantes
- **WebSockets robustos:** Manejo de conexiones con reconexión automática
- **Cache inteligente:** Para llamadas a APIs externas
- **Rate limiting:** Protección contra abuso de endpoints
- **Health checks:** Monitoreo de salud de la aplicación

---

## 3. Autenticación y autorización

- JWT con `Authorization: Bearer <token>`.
- Token genera `sub=id_usuario` y `rol`.
- Dependencias en `core/dependecies.py`:
  - `AdminDep`, `DriverDep`, `RecolectorDep`, `UserDep`.

### 3.1. Roles disponibles

- `admin`: Acceso completo a todas las funcionalidades
- `driver`: Gestión de asignaciones y reportes de ruta
- `recolector`: Visualización de asignaciones y reportes
- `user`: Acceso básico de consulta

### 3.2. Seguridad Optimizada

- **JWT seguro:** Generado con `secrets.token_hex(32)`
- **Expiración configurable:** 480 minutos por defecto
- **Manejo de errores:** 403 para token ausente, 401 para inválido
- **CORS múltiple:** Configurado para desarrollo y producción

---

## 4. Endpoints principales

### 4.1. Autenticación

- `POST /auth/login` - Login con credenciales
- Formato: `application/x-www-form-urlencoded`

### 4.2. Roles (Admin)

- `GET /admin/roles` - Listar roles disponibles en el sistema
- Retorna el catálogo de roles para gestión de usuarios.

### 4.2. Usuarios (Admin)

- `GET /admin/usuarios` - Listar usuarios
- `POST /admin/usuarios` - Crear usuario
- `GET /admin/usuarios/{id}` - Obtener usuario
- `PATCH /admin/usuarios/{id}` - Actualizar usuario
- `DELETE /admin/usuarios/{id}` - Eliminar usuario

### 4.3. Vehículos (Admin)

- `GET /admin/vehiculos` - Listar vehículos
- `POST /admin/vehiculos` - Crear vehículo
- `GET /admin/vehiculos/{id}` - Obtener vehículo
- `PATCH /admin/vehiculos/{id}` - Actualizar vehículo
- `DELETE /admin/vehiculos/{id}` - Eliminar vehículo

### 4.4. Asignaciones

- **Admin:** `GET|POST /admin/asignaciones`
- **Driver:** `GET|POST /driver/asignaciones`
- **Recolector:** `GET|POST /recolector/asignaciones`
- **User:** `GET /user/asignaciones`

### 4.5. Reportes

- `GET /admin/reportes` - Reportes administrativos
- `POST /admin/reportes` - Crear reporte

### 4.6. WebSockets

- `WebSocket /ws/conectar` - Conexión WebSocket con token
- `GET /ws/stats` - Estadísticas de conexiones

### 4.7. Utilidades

- `GET /` - Información de la API
- `GET /health` - Health check
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

---

## 5. Integración con APIs Externas

### 5.1. API de Rutas

- **URL configurable:** `RUTAS_API_URL` en `.env`
- **Validación automática:** Al crear asignaciones
- **Cache implementado:** Para mejorar rendimiento
- **Fallback robusto:** Manejo de errores de red

### 5.2. Ejemplos de Integración

- **Frontend JavaScript:** `ejemplo-frontend.js`
- **Backend Python:** `ejemplo-backend.py`
- **Testing WebSockets:** `test_websockets.py`

---

## 6. Manejo de Errores y Respuestas

### 6.1. Formato Unificado

Todas las respuestas siguen el formato:

**Éxito:**

```json
{
  "success": true,
  "message": "Operación completada",
  "data": { ... }
}
```

**Error:**

```json
{
  "success": false,
  "error": {
    "code": "error_type",
    "message": "Descripción del error",
    "details": null,
    "timestamp": "2026-04-02T..."
  }
}
```

### 6.2. Códigos de Error

- `unauthorized`: Token inválido o expirado
- `forbidden`: Token ausente o permisos insuficientes
- `not_found`: Recurso no encontrado
- `validation_error`: Datos inválidos
- `internal_error`: Error del servidor

---

## 7. Testing y Calidad

### 7.1. Tests Automatizados

- **Cobertura:** 6 tests principales
- **Estado:** ✅ Todos pasan
- **Tipos:** Autenticación, rutas protegidas, WebSockets

### 7.2. Verificación de Calidad

- **Sintaxis:** Todos los archivos verificados
- **Importaciones:** Dependencias correctas
- **Configuración:** Variables de entorno validadas

### 7.3. Rendimiento

- **Benchmarking:** `benchmark_performance.py`
- **Métricas:** Latencia, throughput, concurrencia
- **Optimización:** Async completo, cache, rate limiting

---

## 8. Despliegue y Configuración

### 8.1. Variables de Entorno (.env)

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
SECRET_KEY=clave_secreta_segura
JWT_SECRET=clave_jwt_segura_generada
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
RUTAS_API_URL=http://localhost:8001
```

### 8.2. Comando de Ejecución

```bash
# Desarrollo
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 8.3. Health Checks

- **Endpoint:** `GET /health`
- **Base de datos:** Verificación de conexión
- **APIs externas:** Validación de conectividad

---

## 9. Historial de Optimizaciones

### Versión 1.0.2

- ✅ **Reorganización completa de `main.py`**
- ✅ **Corrección de errores de sintaxis**
- ✅ **Configuración .env segura**
- ✅ **WebSockets optimizados**
- ✅ **Documentación actualizada**
- ✅ **Tests completos y funcionales**

### Correcciones Realizadas

- Sintaxis en archivos de documentación
- Configuración de routers duplicada
- Variables de entorno incompletas
- Contenido HTML en archivos JS
- Indentación incorrecta en código

---

## 10. Contacto y Soporte

- **Desarrolladores:** Jose Luis Prado Valencia, Heiner Jair Godoy Zamora
- **Versión actual:** 1.0.2
- **Documentación:** http://localhost:8000/docs
- **Repositorio:** [GitHub Repository]

### 3.2. Flujo login

- `POST /auth/login`: envía `identifier` (username o correo) + `contraseña`.
- `POST /auth/registro`: registro público con rol `user`.

---

## 4. Formato de respuesta estándar

### 4.1. Respuesta de éxito

```json
{
  "success": true,
  "data": ...,
  "message": "..."
}
```

### 4.2. Respuesta de error

```json
{
  "success": false,
  "error": {
    "code": "not_found|unauthorized|...",
    "message": "...",
    "details": null,
    "path": "/ruta",
    "method": "GET",
    "timestamp": "..."
  }
}
```

---

## 5. Base de datos y modelos principales

### tablas y modelos

- `usuarios` (`Usuario`)
- `roles` (`Rol`, `TipoRol`)
- `perfiles` (`Perfil`)
- `vehiculos` (`Vehiculo`, `EstadoVehiculo`)
- `asignaciones_vehiculo` (`AsignacionVehiculo`, `EstadoAsignacion`)
- `tripulacion_asignacion` (`TripulacionAsignacion`, `RolTripulacion`)
- `reportes` (`ReporteActividad`)

### Enumeraciones

- `EstadoVehiculo`: `disponible`, `en_ruta`, `mantenimiento`, `inactivo`
- `EstadoAsignacion`: `pendiente`, `en_curso`, `completada`, `cancelada`
- `RolTripulacion`: `piloto`, `copiloto`, `recolector`
- `TipoRol`: `admin`, `driver`, `user`, `recolector`

---

## 6. Esquemas (Pydantic)

### 6.1. Autenticación

- `LoginRequest`: `identifier`, `contraseña`
- `TokenResponse`: `access_token`, `token_type` (`bearer`)

### 6.2. Usuarios

- `UsuarioAdminCreate`: `username`, `correo`, `contraseña`, `id_rol`, `activo`
- `UsuarioPublicCreate`: `username`, `correo?`, `contraseña`, `activo`
- `UsuarioUpdate`: campos opcionales `username?`, `correo?`, `contraseña?`, `id_rol?`
- `UsuarioResponse`: respuesta completa con `id_usuario`, `username`, `correo`, `activo`, `id_perfil`, `id_rol`, `perfil`, `rol`, `created_at`, `updated_at`

### 6.3. Vehículos

- `VehiculoCreate`: `placa` (`^[A-Z]{3}\d{3}$`), `modelo?`, `capacidad_m3?`, `estado`
- `VehiculoUpdate`: campos opcionales `placa?`, `modelo?`, `capacidad_m3?`, `estado?`
- `VehiculoResponse`: `id_vehiculo`, `placa`, `modelo`, `capacidad_m3`, `estado`, `created_at`

### 6.4. Asignaciones

- `AsignacionCreate`: `id_vehiculo`, `id_ruta`, `fecha`
- `AsignacionUpdate`: `estado?`, `hora_salida?`
- `AsignacionResponse`: respuesta completa con vehiculo y tripulacion.
- `AsignacionPublicResponse`: consulta pública de ruta: `id_ruta`, `id_vehiculo`, `hora_salida`, `estado`

### 6.5. Tripulación

- `TripulacionCreate`: `id_usuario`, `rol_tripulacion`
- `TripulacionResponse`: detalles del tripulante en asignación

### 6.6. Reportes

- `ReporteCreate`: `id_usuario?`, `u_gmail_cache?`, `u_rol_cache?`, `descripcion`, `asunto`, `evidencia_url?`
- `ReporteResponse`: registro historico con fecha

---

## 7. Endpoints públicos y protegidos (tabla sintetizada)

| Método   | Ruta                                                              | Rol requerido | Request                        | Response                         | Descripción                   |
| -------- | ----------------------------------------------------------------- | ------------- | ------------------------------ | -------------------------------- | ----------------------------- |
| `GET`    | `/`                                                               | público       | -                              | `SuccessResponse`                | health check y version        |
| `GET`    | `/admin/roles`                                                    | `admin`       | -                              | `list[RolResponse]`              | listar roles catálogo         |
| `POST`   | `/auth/login`                                                     | público       | `LoginRequest`                 | `TokenResponse`                  | iniciar sesión                |
| `POST`   | `/auth/registro`                                                  | público       | `UsuarioPublicCreate`          | `UsuarioResponse`                | registrar usuario ciudadano   |
| `POST`   | `/admin/usuarios`                                                 | `admin`       | `UsuarioAdminCreate`           | `UsuarioResponse`                | crear usuario                 |
| `GET`    | `/admin/usuarios`                                                 | `admin`       | -                              | `list[UsuarioResponse]`          | listar usuarios               |
| `GET`    | `/admin/usuarios/{id_usuario}`                                    | `admin`       | -                              | `UsuarioResponse`                | obtener usuario               |
| `PATCH`  | `/admin/usuarios/{id_usuario}`                                    | `admin`       | `UsuarioUpdate`                | `UsuarioResponse`                | actualizar usuario            |
| `DELETE` | `/admin/usuarios/{id_usuario}`                                    | `admin`       | -                              | `{'id_usuario': int}`            | desactivar usuario            |
| `POST`   | `/admin/vehiculos`                                                | `admin`       | `VehiculoCreate`               | `VehiculoResponse`               | crear vehículo                |
| `GET`    | `/admin/vehiculos`                                                | `admin`       | -                              | `list[VehiculoResponse]`         | listar vehículos              |
| `GET`    | `/admin/vehiculos/{id_vehiculo}`                                  | `admin`       | -                              | `VehiculoResponse`               | obtener vehículo              |
| `PATCH`  | `/admin/vehiculos/{id_vehiculo}`                                  | `admin`       | `VehiculoUpdate`               | `VehiculoResponse`               | actualizar vehículo           |
| `PATCH`  | `/admin/vehiculos/{id_vehiculo}/estado`                           | `admin`       | `estado` form/body             | `VehiculoResponse`               | cambiar estado                |
| `DELETE` | `/admin/vehiculos/{id_vehiculo}`                                  | `admin`       | -                              | `{'id_vehiculo': int}`           | eliminar vehículo             |
| `POST`   | `/admin/reportes`                                                 | `admin`       | `ReporteCreate`                | `ReporteResponse`                | registrar reporte             |
| `GET`    | `/admin/reportes`                                                 | `admin`       | query `id_usuario?`, `asunto?` | `list[ReporteResponse]`          | listar reportes               |
| `POST`   | `/admin/asignaciones`                                             | `admin`       | `AsignacionCreate`             | `AsignacionResponse`             | crear asignación              |
| `GET`    | `/admin/asignaciones`                                             | `admin`       | -                              | `list[AsignacionResponse]`       | listar asignaciones           |
| `GET`    | `/admin/asignaciones/rutas/{id_ruta}`                             | `admin`       | -                              | `dict`                           | obtener detalles ruta externa |
| `GET`    | `/admin/asignaciones/{id_asignacion}`                             | `admin`       | -                              | `AsignacionResponse`             | obtener asignación admin      |
| `POST`   | `/admin/asignaciones/{id_asignacion}/cancelar`                    | `admin`       | -                              | `AsignacionResponse`             | cancelar asignación           |
| `POST`   | `/admin/asignaciones/{id_asignacion}/tripulacion`                 | `admin`       | `TripulacionCreate`            | `TripulacionResponse`            | agregar tripulante            |
| `DELETE` | `/admin/asignaciones/{id_asignacion}/tripulacion/{id_usuario}`    | `admin`       | -                              | `{'id_asignacion','id_usuario'}` | eliminar tripulante           |
| `GET`    | `/driver/asignaciones/{id_asignacion}`                            | `driver`      | -                              | `AsignacionResponse`             | ver asignación driver         |
| `POST`   | `/driver/asignaciones/{id_asignacion}/iniciar`                    | `driver`      | -                              | `AsignacionResponse`             | iniciar recorrido             |
| `POST`   | `/driver/asignaciones/{id_asignacion}/finalizar`                  | `driver`      | -                              | `AsignacionResponse`             | finalizar recorrido           |
| `GET`    | `/recolector/asignaciones/{id_asignacion}`                        | `recolector`  | -                              | `AsignacionResponse`             | ver asignación recolector     |
| `POST`   | `/recolector/asignaciones/{id_asignacion}/confirmar/{id_usuario}` | `recolector`  | -                              | `TripulacionResponse`            | confirmar participación       |
| `GET`    | `/rutas/{id_ruta}/horario`                                        | `user`        | -                              | `AsignacionPublicResponse`       | ver horario ruta              |

---

## 8. WebSockets

- `ws://<host>/ws/asignacion/{id_asignacion}?token=<JWT>`
- Se requiere JWT válido con `verificar_token`.
- El canal envía mensajes:
  - `recorrido_iniciado`
  - `recorrido_finalizado`
  - `asignacion_cancelada`

---

## 9. Detalles de implementación relevante

### 9.1 Lifespan

- `main.py` ejecuta `crear_tablas()` antes de aceptar tráfico.

### 9.2 Manejo de errores

- `core/error_handlers.py` define middleware de excepción para generar payload uniforme.

### 9.3 Seguridad de contraseñas

- `core/security.py` usa `passlib` con `bcrypt` y JWT con `pyjwt`.

### 9.4 Dependencias autorizadas

- `require_rol` en `core/dependecies.py` valida el rol del usuario en base al token.

---

## 10. Integración con API externa de rutas

Esta API está preparada para consumir datos de un servicio externo de rutas:

### 10.1 Configuración

- Variable de entorno: `RUTAS_API_URL` (default: `http://localhost:8001`)
- Servicio: `services/service_rutas_externo.py`

### 10.2 Validaciones automáticas

- Al crear asignaciones, se valida que la ruta existe en la API externa
- Endpoint `/admin/asignaciones/rutas/{id_ruta}` para consultar detalles

### 10.3 Flujo esperado

1. Frontend crea ruta en API externa → obtiene `id_ruta`
2. Frontend crea asignación aquí enviando el `id_ruta`
3. Esta API valida que la ruta existe antes de crear la asignación

### 10.4 Manual detallado

Para instrucciones completas de configuración, ejemplos de código y testing, consulta `MANUAL_INTEGRACION_RUTAS.md`.

---

## 11. Análisis de calidad y puntuación de la API

En la auditoría completa del proyecto (routers, controllers, services, schemas, models, core y tests) se verificaron los siguientes puntos:

- Patrón Response uniformizado (`SuccessResponse[T]`) en todos los controllers y routers: ✅
- Patrón Form (`as_form`) aplicado en todos Create/Update y login: ✅
- Patrón Service (instancia en controller, sin singleton global): ✅
- Patrón Guards (Admin/Driver/Recolector/User) aplicado en rutas relevantes: ✅
- Patrón Router (response_model exacto + delete con `dict[str,int]` / `dict[str,str]`): ✅
- Patrón DateTime (timezone=True + default timezone aware): ✅
- Pruebas automáticas (`pytest -q`) cubriendo flujo de auth y roles, CRUD y validaciones: ✅

### 10.1 Puntuación general (0-10)

- Robustez de API: 9.0 (módulos con validación y excepciones bien tratadas)
- Consistencia de contrato: 9.5 (respuestas y tipos alineados)
- Seguridad: 8.5 (JWT + RBAC correctos; zona de mejora: refresh token y rate limit)
- Mantenibilidad: 9.0 (capas limpias, patrones reutilizables, docs actualizadas)

### 10.2 Recomendaciones rápidas

1. Añadir pruebas de integración para WebSocket con token y eventos de cambio de estado.
2. Implementar `rate limit` en rutas de login y creación de recursos para mitigar abuso.
3. Registrar auditoría de eventos sensibles (login fallido, role changes, delete operations).
4. Completar el README con un “change log” de los cambios aplicados (seguridad y respuesta).

---

## 11. Estado actual de tests

Ejecutando `pytest -q` luego de las correcciones:

- `tests/test_api.py`: 6 pasadas, 0 fallos.
- Las pruebas verifican 422/401/403 y los flujos de administrador de usuarios y vehículos.
- Nota: si hay nuevos endpoints, agregar tests de permisos para todos los roles.
