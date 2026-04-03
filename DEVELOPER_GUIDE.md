# 🧠 Guía técnica interna del código

> **Proyecto:** `smart-trash-backend`  
> **Autor del backend:** `Heiner Jair Godoy Zamora`  
> **Propósito de esta guía:** ayudar al equipo a entender el código, mantenerlo y escalarlo con seguridad.

---

## 1. 🎯 Cómo leer este backend

Este proyecto sigue una arquitectura por capas:

```text
Request HTTP/WebSocket
   ↓
Router
   ↓
Controller
   ↓
Service
   ↓
Model / Database
   ↓
Schema de respuesta
```

### Qué hace cada capa

| Capa | Responsabilidad |
|---|---|
| `routers/` | Define las rutas expuestas y el método HTTP |
| `controllers/` | Recibe la petición, aplica dependencias y llama al servicio |
| `services/` | Contiene la lógica de negocio y validaciones reales |
| `models/` | Representa tablas y relaciones en la base de datos |
| `schemas/` | Valida datos de entrada/salida con Pydantic |
| `core/` | Configuración, seguridad, auth y WebSockets |

---

## 2. ⚡ Base técnica importante: API optimizada con `async`

Este backend fue optimizado con programación asíncrona:

- `async def` en routers, controllers y services,
- `AsyncSession` para la base de datos,
- `create_async_engine` con `asyncpg`,
- `verify_password_async()` para no bloquear el event loop,
- WebSockets para eventos en tiempo real.

### ¿Por qué es importante?

Porque permite:

- atender múltiples requests concurrentes,
- evitar bloqueos innecesarios,
- mejorar tiempos de respuesta,
- facilitar escalamiento cuando aumente el número de usuarios.

---

# 3. 📍 Lectura guiada por archivo

## 3.1 `main.py`

### Qué hace
Es el punto de entrada del backend.

### Lectura comentada

- `from fastapi import FastAPI`  
  Importa el framework principal.

- `from fastapi.middleware.cors import CORSMiddleware`  
  Permite que el frontend consuma la API desde otro dominio/puerto.

- `from contextlib import asynccontextmanager`  
  Se usa para manejar el arranque y cierre de la aplicación de forma asíncrona.

- imports de `settings` y routers  
  Cargan la configuración y los módulos de rutas.

- `lifespan(app: FastAPI)`  
  Función asíncrona que corre al iniciar y detener la app.
  - importa `crear_tablas`,
  - crea tablas si no existen,
  - imprime mensajes de control.

- `app = FastAPI(...)`  
  Crea la instancia principal de la API con título y versión.

- `app.add_middleware(CORSMiddleware, ...)`  
  Configura los orígenes permitidos para el frontend.

- `app.include_router(...)`  
  Monta cada módulo de la API:
  - auth,
  - usuarios,
  - vehículos,
  - reportes,
  - asignaciones,
  - WebSockets.

- `@app.get("/")`  
  Endpoint simple para validar que el backend está vivo.

---

## 3.2 `database.py`

### Qué hace
Centraliza la conexión con PostgreSQL usando SQLAlchemy asíncrono.

### Lectura comentada

- `create_async_engine(...)`  
  Crea el motor async de conexión a la base de datos.

- `async_sessionmaker(...)`  
  Crea la fábrica de sesiones `AsyncSession`.

- `Base = declarative_base()`  
  Base que heredan todos los modelos ORM.

- `crear_tablas()`  
  Importa todos los modelos y ejecuta:

```python
await conn.run_sync(Base.metadata.create_all)
```

Esto crea tablas automáticamente en desarrollo.

---

## 3.3 `core/settings.py`

### Qué hace
Lee la configuración desde variables de entorno.

### Variables clave

| Variable | Uso |
|---|---|
| `DATABASE_URL` | conexión a PostgreSQL async |
| `SECRET_KEY` | clave general del sistema |
| `JWT_SECRET` | firma de tokens JWT |
| `JWT_ALGORITHM` | algoritmo de cifrado del token |
| `JWT_EXPIRE_MINUTES` | tiempo de vida del token |
| `CORS_ORIGINS` | dominios permitidos |

### Punto importante

La propiedad `cors_list` convierte una cadena como:

```text
http://localhost:4200,http://localhost:3000
```

en una lista real para FastAPI.

---

## 3.4 `core/security.py`

### Qué hace
Maneja autenticación y seguridad.

### Funciones clave

#### `hash_password(password)`
Convierte una contraseña plana en hash bcrypt.

#### `verify_password(plain, hashed)`
Compara una contraseña plana con su hash.

#### `verify_password_async(plain, hashed)`
Hace lo mismo, pero en un executor asíncrono para no bloquear el servidor.

#### `crear_token(data)`
Genera un JWT y agrega expiración automática.

#### `verificar_token(token)`
Decodifica el JWT y retorna el payload si es válido.

---

## 3.5 `core/dependecies.py`

### Qué hace
Aquí se resuelven tres cosas críticas:

1. la sesión de base de datos,
2. el usuario autenticado,
3. el permiso según rol.

### Flujo real

#### `get_db()`
- abre una sesión `AsyncSession`,
- la entrega al controller/service,
- hace `commit` si todo sale bien,
- hace `rollback` si algo falla.

#### `get_current_user()`
- toma el token Bearer,
- lo valida con `verificar_token()`,
- busca el usuario en BD,
- carga también `rol` y `perfil`.

#### `require_rol(*roles)`
Genera una dependencia para validar autorización.

De ahí salen:
- `AdminDep`
- `DriverDep`
- `RecolectorDep`
- `UserDep`

### `core/error_handlers.py`

Este módulo centraliza el formato de error de toda la API.

Cuando ocurre un `400`, `401`, `403`, `404`, `422` o `500`, la respuesta ahora sigue esta estructura:

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "La solicitud contiene errores de validación.",
    "details": [],
    "path": "/auth/login",
    "method": "POST",
    "timestamp": "2026-03-31T00:00:00+00:00"
  }
}
```

Esto facilita el manejo uniforme desde frontend y hace más predecible la integración.

---

### 3.5.1 `as_form()` para formularios en Swagger

Para los recursos con un request body, ahora se expone cada campo individual en Swagger usando `Form()`. Las entradas de creando y actualización usan `Depends(XxxCreate.as_form)` (o `XxxUpdate.as_form`) en el controller.

- Campos requeridos: `Form(...)`
- Campos opcionales: `Form(None)`
- Retorna: `cls(...)` con todos los datos

Ejemplos:
- `UsuarioAdminCreate.as_form` / `UsuarioUpdate.as_form`
- `VehiculoCreate.as_form` / `VehiculoUpdate.as_form`
- `AsignacionCreate.as_form` / `AsignacionUpdate.as_form`
- `ReporteCreate.as_form`
- `TripulacionCreate.as_form`

Esto habilita un mejor uso de Swagger UI y `application/x-www-form-urlencoded` sin romper las API existentes.

---

## 3.6 `core/websocket_manager.py`

### Qué hace
Administra conexiones WebSocket agrupadas por `id_asignacion`.

### Métodos

- `conectar()` → acepta y registra un socket
- `desconectar()` → lo remueve del grupo
- `broadcast()` → envía eventos JSON a todos los clientes suscritos

### Para qué sirve

Cuando una asignación cambia de estado, todos los clientes conectados reciben el evento sin refrescar la página.

---

# 4. 🌐 Routers: qué expone la API

## 4.1 `routers/router_auth.py`

### Rutas
- `POST /auth/login`
- `POST /auth/registro`

### Función
Exponer acceso público para autenticación y registro.

---

## 4.2 `routers/router_usuarios.py`

### Rutas
- `POST /admin/usuarios/`
- `GET /admin/usuarios/`
- `GET /admin/usuarios/{id_usuario}`
- `PATCH /admin/usuarios/{id_usuario}`
- `DELETE /admin/usuarios/{id_usuario}`

### Función
CRUD administrativo de usuarios.

---

## 4.3 `routers/router_vehiculo.py`

### Rutas
- `POST /admin/vehiculos/`
- `GET /admin/vehiculos/`
- `GET /admin/vehiculos/{id_vehiculo}`
- `PATCH /admin/vehiculos/{id_vehiculo}`
- `PATCH /admin/vehiculos/{id_vehiculo}/estado`
- `DELETE /admin/vehiculos/{id_vehiculo}`

### Función
CRUD y cambio de estado de vehículos.

---

## 4.4 `routers/router_reportes.py`

### Rutas
- `POST /admin/reportes/`
- `GET /admin/reportes/`

### Función
Registrar y consultar reportes del sistema.

---

## 4.5 `routers/router_asignacionvehiculo.py`

### Subrouters
- `router_admin`
- `router_driver`
- `router_recolector`
- `router_user`

### Función
Centraliza toda la operación de rutas y asignaciones por rol.

---

## 4.6 `routers/router_ws.py`

### Ruta
- `WS /ws/asignacion/{id_asignacion}?token=<jwt>`

### Función
Permite escuchar cambios de una asignación en tiempo real.

---

# 5. 🎮 Controllers: qué orquestan

Los controllers son delgados. Su trabajo es:

- recibir la data,
- aplicar dependencias (`Depends`),
- validar autenticación/rol,
- llamar al service correspondiente,
- devolver la respuesta.

## 5.1 `controller_auth.py`

- `login()` → llama `AuthService.login()`
- `registro_publico()` → llama `UsuarioService.registro_publico()`

## 5.2 `controller_usuarios.py`

- `crear_usuario()`
- `listar_usuarios()`
- `obtener_usuario()`
- `actualizar_usuario()`
- `eliminar_usuario()`

Todos requieren `AdminDep`.

## 5.3 `controller_vehiculo.py`

- `crear_vehiculo()`
- `listar_vehiculos()`
- `obtener_vehiculo()`
- `actualizar_vehiculo()`
- `cambiar_estado_vehiculo()`
- `eliminar_vehiculo()`

## 5.4 `controller_reportes.py`

- `crear_reporte()`
- `listar_reportes()` con filtros por `id_usuario` y `asunto`

## 5.5 `controller_asignaciovehiculo.py`

### Admin
- `crear_asignacion()`
- `listar_asignaciones()`
- `obtener_asignacion_admin()`
- `cancelar_asignacion()`
- `agregar_miembro_tripulacion()`
- `eliminar_miembro_tripulacion()`

### Driver
- `ver_asignacion_driver()`
- `iniciar_recorrido()`
- `finalizar_recorrido()`

### Recolector
- `ver_asignacion_recolector()`
- `confirmar_participacion()`

### User
- `ver_horario_ruta()`

---

# 6. 🧠 Services: dónde está la lógica real

## 6.1 `service_auth.py`

### `login(data)`

Hace lo siguiente:

1. busca un usuario por `username` o `correo`,
2. compara la contraseña con `verify_password_async()`,
3. si todo es válido, crea el JWT,
4. devuelve `TokenResponse`.

---

## 6.2 `service_usuarios.py`

### Métodos

- `_check_duplicado()` → evita username/correo repetidos
- `_query_con_relaciones()` → precarga `perfil` y `rol`
- `crear_por_admin()` → crea usuarios operativos
- `registro_publico()` → crea usuarios con rol `user`
- `obtener_todos_usuarios()`
- `obtener_usuario_por_id()`
- `actualizar_usuario()`
- `eliminar_usuario()`

### Reglas importantes

- la contraseña se hashea,
- se crea `Perfil` automáticamente,
- no se permite desactivar un admin.

---

## 6.3 `service_vehiculo.py`

### Métodos

- `añadir_vehiculo()`
- `obtener_todos_vehiculos()`
- `obtener_vehiculo_por_id()`
- `actualizar_vehiculo_por_id()`
- `cambiar_estado_vehiculo()`
- `eliminar_vehiculo()`

### Regla clave

La placa debe ser única.

---

## 6.4 `service_reportes.py`

### Métodos

- `registrar_reporte()` → crea un registro de actividad
- `obtener_reportes()` → permite filtros y orden descendente por fecha

---

## 6.5 `service_asignaciovehiculo.py`

### Métodos

- `_con_relaciones()` → carga vehículo y tripulación
- `crear_asignacion()`
- `obtener_asignaciones()`
- `obtener_asignacion_id()`
- `obtener_asignacion_ruta()`
- `verificar_asignacion_pendiente()`
- `iniciar_recorrido()`
- `finalizar_recorrido()`
- `cancelar_asignacion()`

### Reglas de negocio críticas

#### `crear_asignacion()`
- valida que el vehículo exista,
- valida que esté `disponible`,
- crea una asignación con estado `pendiente`.

#### `iniciar_recorrido()`
- solo inicia si la asignación está `pendiente`,
- exige que toda la tripulación confirme,
- cambia el vehículo a `en_ruta`,
- emite WebSocket `recorrido_iniciado`.

#### `finalizar_recorrido()`
- solo permite finalizar si está `en_curso`,
- cambia vehículo a `disponible`,
- emite `recorrido_finalizado`.

#### `cancelar_asignacion()`
- no deja cancelar si ya fue completada,
- regresa el vehículo a `disponible`,
- emite `asignacion_cancelada`.

---

## 6.6 `service_tripulacionasignada.py`

### Métodos

- `_verificar_asignacion_pendiente()`
- `agregar_miembro()`
- `confirmar_asignacion()`
- `eliminar_miembro_asignacion()`

### Reglas clave

- solo se puede editar tripulación si la asignación está `pendiente`,
- el usuario no puede agregarse dos veces,
- cada confirmación queda registrada con fecha,
- al confirmar, se emite el evento `tripulacion_confirmo`.

---

# 7. 🗃️ Models: cómo se organiza la base de datos

## Tablas principales

| Modelo | Finalidad |
|---|---|
| `Usuario` | usuarios del sistema |
| `Rol` | catálogo de roles |
| `Perfil` | datos base asociados al usuario |
| `Vehiculo` | camiones recolectores |
| `AsignacionVehiculo` | relación entre vehículo y ruta externa |
| `TripulacionAsignacion` | miembros asignados a una ruta |
| `ReporteActividad` | bitácora/reportes del sistema |

### Relación más importante

```text
Rol ──< Usuario >── Perfil
Usuario ──< ReporteActividad
Usuario ──< TripulacionAsignacion >── AsignacionVehiculo >── Vehiculo
```

---

# 8. ✅ Schemas: qué entra y qué sale en la API

## Ejemplos por módulo

### Auth
- `LoginRequest`
- `TokenResponse`

### Usuarios
- `UsuarioAdminCreate`
- `UsuarioPublicCreate`
- `UsuarioUpdate`
- `UsuarioResponse`

### Vehículos
- `VehiculoCreate`
- `VehiculoUpdate`
- `VehiculoResponse`

### Reportes
- `ReporteCreate`
- `ReporteResponse`

### Asignaciones
- `AsignacionCreate`
- `AsignacionResponse`
- `AsignacionPublicResponse`

### Tripulación
- `TripulacionCreate`
- `TripulacionResponse`

---

# 9. 🔌 Flujo real de una petición

## Ejemplo: crear una asignación

```text
POST /admin/asignaciones/
   ↓
router_admin.post(...)
   ↓
controller_asignaciovehiculo.crear_asignacion()
   ↓
AsignacionService.crear_asignacion()
   ↓
Valida vehículo + estado disponible
   ↓
Guarda en la BD con AsyncSession
   ↓
Devuelve AsignacionResponse
```

## Ejemplo: iniciar un recorrido

```text
POST /driver/asignaciones/{id}/iniciar
   ↓
Driver autenticado
   ↓
Controller
   ↓
AsignacionService.iniciar_recorrido()
   ↓
Valida estado + confirmaciones
   ↓
Actualiza asignación y vehículo
   ↓
Envía evento WebSocket
   ↓
Respuesta al cliente
```

---

# 10. 🚀 Consejos para escalar esta API

## 10.1 Mantener separación por capas
No mezclar lógica de negocio dentro de routers.

## 10.2 Crear nuevos módulos siguiendo el patrón actual
Si en el futuro agregas, por ejemplo, `notificaciones`:

```text
models/model_notificacion.py
schemas/schema_notificacion.py
services/service_notificacion.py
controllers/controller_notificacion.py
routers/router_notificacion.py
```

## 10.3 Fortalecer para producción

Recomendaciones:

- añadir pruebas automatizadas,
- usar logs estructurados,
- mover `create_all()` fuera del arranque en producción,
- usar migraciones Alembic únicamente,
- agregar paginación,
- estandarizar respuestas de error,
- añadir caché si crece la consulta de rutas externas.

## 10.4 WebSockets y concurrencia
Si aumenta el tráfico:

- usar Redis Pub/Sub o un broker,
- desacoplar eventos en tiempo real,
- monitorear conexiones activas por asignación.

---

# 11. 🧩 Recomendación práctica para el equipo

Si alguien nuevo entra al proyecto, el orden ideal para entender el backend es:

1. `main.py`
2. `database.py`
3. `core/settings.py`
4. `core/security.py`
5. `core/dependecies.py`
6. `routers/`
7. `controllers/`
8. `services/`
9. `models/`
10. `schemas/`

---

# 12. ✅ Conclusión

Este backend ya tiene una base sólida para crecer porque:

- está organizado por responsabilidades,
- usa FastAPI asíncrono,
- separa autenticación, negocio y persistencia,
- y ya dispone de WebSockets para eventos en tiempo real.

Para mantenimiento del equipo, esta guía debe leerse junto con:

- `README.md`
- `API_DOCUMENTATION.md`
- `http://localhost:8000/docs`

---

> **Nota:** esta guía comenta el código por bloques lógicos y funciones principales, que es la forma más útil de explicar “línea por línea” sin volver el repositorio difícil de mantener.