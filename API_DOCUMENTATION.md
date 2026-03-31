# 📘 Documentación técnica y funcional de la API

> **Proyecto:** `smart-trash-backend`  
> **Framework:** FastAPI  
> **Versión declarada en la app:** `1.0.0`  
> **Autor del backend:** `Heiner Jair Godoy Zamora`  
> **Fecha de revisión:** `31 de marzo de 2026`

---

## 📎 Documentación complementaria para el equipo

Para entender el código con más profundidad y facilitar mantenimiento o escalabilidad, revisa también:

- [`DEVELOPER_GUIDE.md`](./DEVELOPER_GUIDE.md) → guía interna, comentada por módulos y flujo de ejecución.

---

## 1. ✅ Resumen ejecutivo

Esta API backend soporta el sistema **Smart Trash Route**, una plataforma para gestionar:

- autenticación de usuarios,
- administración de usuarios y roles,
- gestión de vehículos recolectores,
- registro de reportes,
- asignación de vehículos a rutas,
- confirmación de tripulación,
- seguimiento del estado operativo de los recorridos.

La aplicación está construida con una arquitectura por capas:

- `routers/` → expone los endpoints HTTP,
- `controllers/` → conecta rutas con la lógica,
- `services/` → implementa reglas de negocio,
- `models/` → define tablas y relaciones SQLAlchemy,
- `schemas/` → define contratos de entrada/salida con Pydantic,
- `core/` → seguridad, configuración, dependencias y WebSockets.

Además, esta API fue **optimizada con programación asíncrona (`async`/`await`)**, lo que permite manejar operaciones de base de datos, autenticación y comunicación en tiempo real de forma más eficiente y sin bloquear el flujo del servidor.
---

## 2. 🧱 Arquitectura del proyecto

### Flujo interno de una petición

```text
Cliente HTTP
   ↓
Router (`routers/`)
   ↓
Controller (`controllers/`)
   ↓
Service (`services/`)
   ↓
Model + DB (`models/`, `database.py`)
   ↓
Schema de respuesta (`schemas/`)
```

### Archivos clave revisados

| Archivo | Función |
|---|---|
| `main.py` | Crea la app FastAPI, CORS y registra routers con `lifespan` asíncrono |
| `core/dependecies.py` | Manejo de sesión DB, JWT y autorización por rol |
| `core/security.py` | Hash de contraseñas y validación JWT, incluyendo verificación async |
| `database.py` | Engine async SQLAlchemy y creación de tablas |
| `routers/*.py` | Definición pública de endpoints |
| `services/*.py` | Reglas de negocio y validaciones asíncronas |

### ⚡ Optimización asíncrona de la API

Esta API fue diseñada para aprovechar el modelo **asíncrono** de FastAPI:

- uso de `async def` en controladores y servicios,
- conexión a base de datos con `AsyncSession`,
- motor SQLAlchemy con `create_async_engine`,
- manejo no bloqueante del ciclo de vida de la app con `@asynccontextmanager`,
- verificación de contraseñas con `verify_password_async()`,
- soporte de comunicación en tiempo real mediante WebSockets.

Esto mejora la capacidad de respuesta del backend cuando existen múltiples peticiones concurrentes.

---

## 3. 🌐 Información general de despliegue

### Base URL local

```http
http://localhost:8000
```

### Endpoints automáticos de FastAPI

| Endpoint | Descripción |
|---|---|
| `GET /` | Mensaje de bienvenida |
| `GET /docs` | Swagger UI |
| `GET /redoc` | ReDoc |
| `GET /openapi.json` | Especificación OpenAPI generada automáticamente |

### Respuesta de raíz

**`GET /`**

```json
{
  "message": "Bienvenido a la API Smart Trash Route!"
}
```

---

## 4. 🔐 Autenticación y autorización

La API usa **JWT Bearer Token**.

### Flujo de autenticación

1. El usuario se registra o inicia sesión.
2. `POST /auth/login` devuelve `access_token`.
3. El cliente envía el token en el header:

```http
Authorization: Bearer <token>
```

### Esquema de seguridad

El backend usa `HTTPBearer()` y valida el token en `core/dependecies.py`.

### Roles soportados

| Rol | Valor interno | Uso |
|---|---|---|
| Administrador | `admin` | Gestiona usuarios, vehículos, reportes y asignaciones |
| Conductor | `driver` | Visualiza asignación y cambia estado del recorrido |
| Recolector | `recolector` | Confirma participación en asignación |
| Ciudadano/usuario | `user` | Consulta horario de rutas |

### Códigos de error frecuentes de seguridad

| Código | Motivo |
|---|---|
| `401` | Token inválido, expirado o usuario inexistente |
| `403` | El usuario autenticado no tiene el rol requerido |
| `422` | Faltan campos o tipos válidos en la petición |

---

## 5. 🧩 Enumeraciones del sistema

### `TipoRol`

```text
admin | driver | user | recolector
```

### `EstadoVehiculo`

```text
disponible | en_ruta | mantenimiento | inactivo
```

### `EstadoAsignacion`

```text
pendiente | en_curso | completada | cancelada
```

### `RolTripulacion`

```text
piloto | copiloto | recolector
```

---

## 6. 📚 Mapa general de endpoints

| Método | Ruta | Rol requerido | Descripción |
|---|---|---|---|
| `GET` | `/` | Público | Bienvenida |
| `POST` | `/auth/login` | Público | Iniciar sesión |
| `POST` | `/auth/registro` | Público | Registro público de usuario |
| `POST` | `/admin/usuarios/` | `admin` | Crear usuario por admin |
| `GET` | `/admin/usuarios/` | `admin` | Listar usuarios |
| `GET` | `/admin/usuarios/{id_usuario}` | `admin` | Obtener usuario |
| `PATCH` | `/admin/usuarios/{id_usuario}` | `admin` | Actualizar usuario |
| `DELETE` | `/admin/usuarios/{id_usuario}` | `admin` | Desactivar usuario |
| `POST` | `/admin/vehiculos/` | `admin` | Crear vehículo |
| `GET` | `/admin/vehiculos/` | `admin` | Listar vehículos |
| `GET` | `/admin/vehiculos/{id_vehiculo}` | `admin` | Obtener vehículo |
| `PATCH` | `/admin/vehiculos/{id_vehiculo}` | `admin` | Actualizar vehículo |
| `PATCH` | `/admin/vehiculos/{id_vehiculo}/estado` | `admin` | Cambiar estado del vehículo |
| `DELETE` | `/admin/vehiculos/{id_vehiculo}` | `admin` | Eliminar vehículo |
| `POST` | `/admin/reportes/` | `admin` | Crear reporte |
| `GET` | `/admin/reportes/` | `admin` | Listar reportes con filtros |
| `POST` | `/admin/asignaciones/` | `admin` | Crear asignación de vehículo a ruta |
| `GET` | `/admin/asignaciones/` | `admin` | Listar asignaciones |
| `GET` | `/admin/asignaciones/{id_asignacion}` | `admin` | Obtener asignación |
| `POST` | `/admin/asignaciones/{id_asignacion}/cancelar` | `admin` | Cancelar asignación |
| `POST` | `/admin/asignaciones/{id_asignacion}/tripulacion` | `admin` | Agregar miembro a tripulación |
| `DELETE` | `/admin/asignaciones/{id_asignacion}/tripulacion/{id_usuario}` | `admin` | Eliminar miembro de tripulación |
| `GET` | `/driver/asignaciones/{id_asignacion}` | `driver` | Ver asignación como conductor |
| `POST` | `/driver/asignaciones/{id_asignacion}/iniciar` | `driver` | Iniciar recorrido |
| `POST` | `/driver/asignaciones/{id_asignacion}/finalizar` | `driver` | Finalizar recorrido |
| `GET` | `/recolector/asignaciones/{id_asignacion}` | `recolector` | Ver asignación como recolector |
| `POST` | `/recolector/asignaciones/{id_asignacion}/confirmar/{id_usuario}` | `recolector` | Confirmar participación |
| `GET` | `/rutas/{id_ruta}/horario` | `user` | Consultar horario de una ruta |

> **Nota:** las rutas de creación principales ya responden con `201 Created`, alineadas con las buenas prácticas REST.

---

# 7. 🔑 Módulo de autenticación

## 7.1 `POST /auth/login`

Inicia sesión usando `username` o `correo` en el campo `identifier`.

### Body

```json
{
  "identifier": "admin",
  "contraseña": "admin123"
}
```

### Reglas

- `identifier` puede ser username o correo.
- La contraseña se valida contra el hash almacenado.
- Si las credenciales son válidas, se genera JWT con:
  - `sub`: ID del usuario
  - `rol`: ID del rol
  - `exp`: expiración según `JWT_EXPIRE_MINUTES`

### Respuesta exitosa

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### Errores esperados

| Código | Detalle |
|---|---|
| `401` | `Credenciales incorrectas` |
| `422` | Payload inválido |

### Ejemplo `curl`

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"admin","contraseña":"admin123"}'
```

---

## 7.2 `POST /auth/registro`

Registra un usuario público con rol automático `user`.

### Body

```json
{
  "username": "ciudadano01",
  "correo": "ciudadano01@example.com",
  "contraseña": "clave123",
  "activo": true
}
```

### Reglas de negocio

- `username`: mínimo 3 caracteres.
- `correo`: validación de email y conversión a minúsculas.
- `contraseña`: mínimo 6 caracteres.
- El rol se asigna automáticamente como `user`.
- Se crea también un `Perfil` asociado.

### Respuesta

Devuelve un objeto `UsuarioResponse` con:

- `id_usuario`
- `username`
- `correo`
- `activo`
- `id_perfil`
- `id_rol`
- `perfil`
- `rol`
- `created_at`
- `updated_at`

### Errores esperados

| Código | Detalle |
|---|---|
| `400` | `El username o correo ya está en uso` |
| `500` | `Rol 'user' no configurado en el sistema` |
| `422` | Error de validación |

> **Observación de revisión:** aunque `correo` aparece como opcional en `UsuarioPublicCreate`, el modelo de base de datos lo define como no nulo. En la práctica se recomienda enviarlo siempre.

---

# 8. 👥 Módulo de usuarios (`admin`)

Prefijo base: ` /admin/usuarios `

## 8.1 `POST /admin/usuarios/`

Crea usuarios administrativos o de operación.

### Body

```json
{
  "username": "driver01",
  "correo": "driver01@example.com",
  "contraseña": "clave123",
  "id_rol": 2,
  "activo": true
}
```

### Reglas

- Requiere token con rol `admin`.
- Verifica duplicados por `username` o `correo`.
- Verifica que el rol exista.
- Crea perfil automáticamente usando el username como nombre.
- La contraseña se almacena hasheada.

### Posibles respuestas de error

| Código | Detalle |
|---|---|
| `400` | `El username o correo ya está en uso` |
| `400` | `Rol no encontrado` |
| `401` | Token inválido |
| `403` | Sin permisos |

---

## 8.2 `GET /admin/usuarios/`

Lista todos los usuarios con su `perfil` y `rol` cargados.

### Respuesta

```json
[
  {
    "id_usuario": 1,
    "username": "admin",
    "correo": "admin@test.com",
    "activo": true,
    "id_perfil": 1,
    "id_rol": 1,
    "perfil": {
      "id_perfil": 1,
      "nombre": "Administrador",
      "id_rol": 1,
      "rol": {
        "id_rol": 1,
        "nombre": "admin"
      }
    },
    "rol": {
      "id_rol": 1,
      "nombre": "admin"
    },
    "created_at": "2026-03-31T10:00:00Z",
    "updated_at": "2026-03-31T10:00:00Z"
  }
]
```

---

## 8.3 `GET /admin/usuarios/{id_usuario}`

Obtiene un usuario por ID.

### Parámetros de ruta

| Nombre | Tipo | Requerido |
|---|---|---|
| `id_usuario` | `int` | Sí |

### Errores

| Código | Detalle |
|---|---|
| `404` | `Usuario no encontrado` |

---

## 8.4 `PATCH /admin/usuarios/{id_usuario}`

Actualiza campos parciales del usuario.

### Body permitido

```json
{
  "username": "nuevo_username",
  "correo": "nuevo@example.com",
  "contraseña": "nueva_clave123",
  "id_rol": 3
}
```

### Reglas

- Solo actualiza los campos enviados.
- Si se envía `contraseña`, se re-hashea antes de guardar.

---

## 8.5 `DELETE /admin/usuarios/{id_usuario}`

Desactiva al usuario cambiando `activo = false`.

### Respuesta

```json
{
  "message": "Usuario eliminado"
}
```

### Reglas importantes

- No elimina físicamente el registro.
- No permite desactivar usuarios con rol `admin`.

### Error específico

| Código | Detalle |
|---|---|
| `400` | `No se puede eliminar un usuario con rol de administrador` |

---

# 9. 🚚 Módulo de vehículos (`admin`)

Prefijo base: ` /admin/vehiculos `

## 9.1 `POST /admin/vehiculos/`

Crea un vehículo recolector.

### Body

```json
{
  "placa": "ABC123",
  "modelo": "Hino 2022",
  "capacidad_m3": 12.5,
  "estado": "disponible"
}
```

### Reglas

- La `placa` debe ser única.
- El `estado` por defecto es `disponible`.

### Errores

| Código | Detalle |
|---|---|
| `400` | `Ya existe un vehículo con esa placa` |

---

## 9.2 `GET /admin/vehiculos/`

Lista todos los vehículos.

### Respuesta ejemplo

```json
[
  {
    "id_vehiculo": 1,
    "placa": "ABC123",
    "modelo": "Hino 2022",
    "capacidad_m3": 12.5,
    "estado": "disponible",
    "created_at": "2026-03-31T10:00:00Z"
  }
]
```

---

## 9.3 `GET /admin/vehiculos/{id_vehiculo}`

Obtiene un vehículo específico.

### Error específico

| Código | Detalle |
|---|---|
| `404` | `Vehículo no encontrado` |

---

## 9.4 `PATCH /admin/vehiculos/{id_vehiculo}`

Actualiza parcialmente el vehículo.

### Body

```json
{
  "modelo": "Isuzu 2024",
  "capacidad_m3": 15,
  "estado": "mantenimiento"
}
```

---

## 9.5 `PATCH /admin/vehiculos/{id_vehiculo}/estado`

Cambia únicamente el estado del vehículo.

### Importante

El parámetro `estado` se recibe como **query parameter**, no como body JSON.

### Ejemplo

```http
PATCH /admin/vehiculos/1/estado?estado=en_ruta
```

### Valores válidos

```text
disponible | en_ruta | mantenimiento | inactivo
```

---

## 9.6 `DELETE /admin/vehiculos/{id_vehiculo}`

Elimina físicamente el vehículo.

### Respuesta

```json
{
  "message": "Vehículo eliminado"
}
```

---

# 10. 📝 Módulo de reportes (`admin`)

Prefijo base: ` /admin/reportes `

## 10.1 `POST /admin/reportes/`

Registra un reporte de actividad.

### Body

```json
{
  "id_usuario": 2,
  "u_gmail_cache": "driver01@example.com",
  "u_rol_cache": "driver",
  "descripcion": "Se reporta demora en la salida del vehículo.",
  "asunto": "demora_operativa",
  "evidencia_url": "https://ejemplo.com/evidencia.jpg"
}
```

### Campos

| Campo | Tipo | Requerido | Nota |
|---|---|---|---|
| `id_usuario` | `int \| null` | No | ID del usuario relacionado |
| `u_gmail_cache` | `str \| null` | No | Correo guardado como cache |
| `u_rol_cache` | `str \| null` | No | Rol cacheado |
| `descripcion` | `str` | Sí | Descripción del evento |
| `asunto` | `str` | Sí | Categoría o asunto del reporte |
| `evidencia_url` | `str \| null` | No | URL de evidencia |

---

## 10.2 `GET /admin/reportes/`

Lista reportes y permite filtros opcionales.

### Query params

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `id_usuario` | `int` | No | Filtra por usuario |
| `asunto` | `string` | No | Filtra por asunto exacto |

### Ejemplos

```http
GET /admin/reportes/
GET /admin/reportes/?id_usuario=2
GET /admin/reportes/?asunto=demora_operativa
```

### Orden

Los reportes se devuelven ordenados por `fecha DESC`.

---

# 11. 🗺️ Módulo de asignaciones (`admin`, `driver`, `recolector`, `user`)

Las asignaciones conectan un vehículo con una ruta (`id_ruta`) y una fecha de operación.

> **Importante:** el valor de `id_ruta` **no lo genera este backend**. Ese identificador es **asignado por una API externa** de rutas, y este proyecto solo lo almacena y lo usa como referencia para consultar/relacionar la operación local.

## 11.1 `POST /admin/asignaciones/`

Crea una asignación de vehículo a una ruta.

### Body

```json
{
  "id_vehiculo": 1,
  "id_ruta": "RUTA-CENTRO-01",
  "fecha": "2026-03-31T06:00:00Z"
}
```

### Reglas de negocio

- El vehículo debe existir.
- El vehículo debe estar en estado `disponible`.
- `id_ruta` debe venir previamente asignado por la **API externa** de rutas.
- La asignación nace en estado `pendiente`.

### Errores

| Código | Detalle |
|---|---|
| `404` | `Vehículo no encontrado` |
| `400` | `El vehículo no está disponible...` |

---

## 11.2 `GET /admin/asignaciones/`

Lista todas las asignaciones con:

- datos del vehículo,
- estado actual,
- fecha,
- hora de salida,
- tripulación asociada.

### Respuesta ejemplo

```json
[
  {
    "id_asignacion": 10,
    "id_vehiculo": 1,
    "id_ruta": "RUTA-CENTRO-01",
    "fecha": "2026-03-31T06:00:00Z",
    "hora_salida": null,
    "estado": "pendiente",
    "created_at": "2026-03-31T05:40:00Z",
    "vehiculo": {
      "id_vehiculo": 1,
      "placa": "ABC123",
      "modelo": "Hino 2022",
      "capacidad_m3": 12.5,
      "estado": "disponible",
      "created_at": "2026-03-30T12:00:00Z"
    },
    "tripulacion": []
  }
]
```

---

## 11.3 `GET /admin/asignaciones/{id_asignacion}`

Obtiene el detalle completo de una asignación específica.

### Error

| Código | Detalle |
|---|---|
| `404` | `Asignación no encontrada` |

---

## 11.4 `POST /admin/asignaciones/{id_asignacion}/cancelar`

Cancela una asignación.

### Reglas

- No permite cancelar una asignación ya `completada`.
- Al cancelar, el vehículo vuelve a `disponible`.
- Genera evento WebSocket `asignacion_cancelada`.

### Error

| Código | Detalle |
|---|---|
| `400` | `No se puede cancelar una asignación ya completada` |

---

## 11.5 `POST /admin/asignaciones/{id_asignacion}/tripulacion`

Agrega un miembro a la tripulación.

### Body

```json
{
  "id_usuario": 5,
  "rol_tripulacion": "recolector"
}
```

### Reglas

- Solo se permite si la asignación está `pendiente`.
- No se puede agregar dos veces el mismo usuario a la misma asignación.

### Errores

| Código | Detalle |
|---|---|
| `404` | `Asignación no encontrada` |
| `400` | `Solo se puede modificar la tripulación de una asignación pendiente` |
| `400` | `El usuario ya está en esta asignación` |

---

## 11.6 `DELETE /admin/asignaciones/{id_asignacion}/tripulacion/{id_usuario}`

Elimina a un miembro de la tripulación.

### Reglas esperadas

- Solo debería permitirse si la asignación sigue `pendiente`.
- Devuelve:

```json
{
  "message": "Miembro eliminado de la tripulación"
}
```

---

## 11.7 `GET /driver/asignaciones/{id_asignacion}`

Permite al conductor ver la asignación que le corresponde.

### Rol requerido

`driver`

---

## 11.8 `POST /driver/asignaciones/{id_asignacion}/iniciar`

Marca el recorrido como iniciado.

### Reglas de negocio

- La asignación debe estar en `pendiente`.
- **Toda la tripulación debe haber confirmado** antes de iniciar.
- Al iniciar:
  - `estado = en_curso`
  - `hora_salida = now()`
  - `vehiculo.estado = en_ruta`
- Emite evento WebSocket `recorrido_iniciado`.

### Errores

| Código | Detalle |
|---|---|
| `400` | `Solo se puede iniciar una asignación en estado pendiente` |
| `400` | `Toda la tripulación debe confirmar antes de iniciar` |

---

## 11.9 `POST /driver/asignaciones/{id_asignacion}/finalizar`

Finaliza el recorrido.

### Reglas de negocio

- Solo puede finalizarse si está `en_curso`.
- Al finalizar:
  - `estado = completada`
  - `vehiculo.estado = disponible`
- Emite evento WebSocket `recorrido_finalizado`.

### Error

| Código | Detalle |
|---|---|
| `400` | `Solo se puede finalizar una asignación en curso` |

---

## 11.10 `GET /recolector/asignaciones/{id_asignacion}`

Permite a un recolector consultar la asignación asociada.

### Rol requerido

`recolector`

---

## 11.11 `POST /recolector/asignaciones/{id_asignacion}/confirmar/{id_usuario}`

Confirma la participación de un miembro de tripulación.

### Reglas

- Debe existir el registro de `TripulacionAsignacion`.
- Si ya estaba confirmado, responde error.
- Al confirmar:
  - `confirmado = true`
  - `confirmado_at = now()`
- Emite evento WebSocket `tripulacion_confirmo`.

### Errores

| Código | Detalle |
|---|---|
| `404` | `No perteneces a esta asignación` |
| `400` | `Ya confirmaste tu participación` |

---

## 11.12 `GET /rutas/{id_ruta}/horario`

Endpoint orientado al ciudadano para consultar el horario de una ruta.

### Rol requerido

`user`

### Respuesta

```json
{
  "id_ruta": "RUTA-CENTRO-01",
  "id_vehiculo": 1,
  "hora_salida": "2026-03-31T06:05:00Z",
  "estado": "en_curso"
}
```

### Error

| Código | Detalle |
|---|---|
| `404` | `Ruta no encontrada` |

---

# 12. 🔌 WebSockets

Existe soporte de WebSocket en `router_ws.py`.

## Endpoint definido en código

```text
/ws/asignacion/{id_asignacion}?token=<jwt>
```

## Funcionamiento

- Valida el JWT antes de aceptar la conexión.
- Agrupa conexiones por `id_asignacion`.
- Envía eventos JSON cuando cambia el estado de la asignación o la tripulación.

## Eventos emitidos

### `tripulacion_confirmo`

```json
{
  "evento": "tripulacion_confirmo",
  "id_asignacion": 10,
  "id_usuario": 5,
  "rol": "recolector"
}
```

### `recorrido_iniciado`

```json
{
  "evento": "recorrido_iniciado",
  "id_asignacion": 10,
  "hora_salida": "2026-03-31T06:05:00+00:00",
  "estado": "en_curso"
}
```

### `recorrido_finalizado`

```json
{
  "evento": "recorrido_finalizado",
  "id_asignacion": 10,
  "estado": "completada"
}
```

### `asignacion_cancelada`

```json
{
  "evento": "asignacion_cancelada",
  "id_asignacion": 10,
  "estado": "cancelada"
}
```

> **Observación importante:** el router WebSocket existe, pero en `main.py` no se está incluyendo `router_ws`, por lo que ese endpoint no queda montado automáticamente en la app actual.

---

# 13. 🗃️ Modelos de datos principales

## `Usuario`

Campos principales:

- `id_usuario`
- `id_perfil`
- `id_rol`
- `username`
- `correo`
- `contraseña`
- `activo`
- `created_at`
- `updated_at`

## `Rol`

- `id_rol`
- `nombre`

## `Perfil`

- `id_perfil`
- `id_rol`
- `nombre`

## `Vehiculo`

- `id_vehiculo`
- `placa`
- `modelo`
- `capacidad_m3`
- `estado`
- `created_at`

## `AsignacionVehiculo`

- `id_asignacion`
- `id_vehiculo`
- `id_ruta`
- `hora_salida`
- `fecha`
- `estado`
- `created_at`

## `TripulacionAsignacion`

- `id`
- `id_asignacion`
- `id_usuario`
- `rol_tripulacion`
- `confirmado`
- `confirmado_at`

## `ReporteActividad`

- `id_registro`
- `id_usuario`
- `u_gmail_cache`
- `u_rol_cache`
- `descripcion`
- `asunto`
- `evidencia_url`
- `fecha`

---

# 14. ⚙️ Variables de entorno relevantes

Tomadas de `core/settings.py`:

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Conexión a PostgreSQL/PostGIS con driver async |
| `SECRET_KEY` | Clave general del proyecto |
| `JWT_SECRET` | Clave para firmar JWT |
| `JWT_ALGORITHM` | Algoritmo JWT, default `HS256` |
| `JWT_EXPIRE_MINUTES` | Duración del token, default `480` |
| `CORS_ORIGINS` | Orígenes permitidos, default `http://localhost:4200` |

---

# 15. 🧪 Recomendaciones de uso desde frontend o Postman

## Header común autenticado

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Orden recomendado de prueba funcional

1. Registrar o sembrar un usuario admin.
2. Hacer login con `POST /auth/login`.
3. Crear usuarios operativos (`driver`, `recolector`).
4. Crear vehículo.
5. Crear asignación.
6. Agregar tripulación.
7. Confirmar participación desde el rol `recolector`.
8. Iniciar recorrido desde el rol `driver`.
9. Finalizar recorrido.
10. Consultar la ruta desde `/rutas/{id_ruta}/horario`.

---

# 16. 🔍 Hallazgos de la revisión técnica del código

Además de documentar la API, durante la revisión se detectaron estas observaciones importantes:

## 16.1 Inconsistencias de nombres entre controladores y servicios

Hay referencias que **parecen no coincidir** con los nombres definidos en servicios, por ejemplo:

- `controller_vehiculo.py` llama `actualizar_vehiculo_by_id`, pero en `service_vehiculo.py` aparece `update_vehiculo_por_id`.
- `controller_asignaciovehiculo.py` llama `AsignacionService(db).crear(...)`, pero en `service_asignaciovehiculo.py` está definido `crear_asignacion(...)`.
- `controller_asignaciovehiculo.py` llama `TripulacionService(db).eliminar_miembro(...)`, pero en `service_tripulacionasignada.py` se define `eliminar_miembro_asignacion(...)`.

### Impacto posible

Algunos endpoints podrían fallar en tiempo de ejecución si esas rutas son invocadas sin corregir esos nombres.

## 16.2 WebSocket no montado en `main.py`

Aunque existe `router_ws.py`, no se hace `app.include_router(...)` para él.

## 16.3 Registro público con `correo` opcional

El schema `UsuarioPublicCreate` permite `correo = null`, pero el modelo `Usuario` lo requiere como `nullable=False`.

---

# 17. 🚀 Mejoras sugeridas para la API

1. Definir `status_code=201` en endpoints de creación.
2. Agregar `summary`, `description` y ejemplos directamente en cada ruta FastAPI.
3. Corregir las inconsistencias de nombres entre controladores y servicios.
4. Montar el router WebSocket en `main.py` si se va a usar en producción.
5. Añadir paginación y búsqueda más flexible para listados.
6. Estandarizar respuestas de error.
7. Añadir pruebas automáticas de integración para cada módulo.

---

# 18. ✅ Conclusión

La API tiene una base clara y bien separada por capas, con soporte para autenticación por JWT, control de acceso por roles y gestión del ciclo operativo de rutas de recolección.

Su dominio principal gira alrededor de:

- usuarios,
- vehículos,
- reportes,
- asignaciones,
- tripulación,
- seguimiento del estado de rutas.

Para desarrollo y consumo, la referencia rápida sigue siendo:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

Y esta guía complementa esa referencia con contexto funcional, reglas de negocio y observaciones de implementación.
