# 📘 Documentación Completa del Backend - Smart Trash Route

> **Proyecto:** `smart-trash-backend`
> **Framework:** FastAPI
> **Versión:** `1.0.3`
> **Autor:** `Heiner Jair Godoy Zamora y Jose Luis Prado Valencia`
> **Fecha de revisión:** `23 de abril de 2026`

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Módulos y Entidades](#3-módulos-y-entidades)
4. [Endpoints REST API](#4-endpoints-rest-api)
5. [Modelos de Datos](#5-modelos-de-datos)
6. [Esquemas Pydantic](#6-esquemas-pydantic)
7. [Ejemplos de Peticiones y Respuestas](#7-ejemplos-de-peticiones-y-respuestas)
8. [Funcionalidades Críticas](#8-funcionalidades-críticas)
9. [Estado de Implementación](#9-estado-de-implementación)
10. [WebSockets](#10-websockets)

---

## 1. Resumen Ejecutivo

Smart Trash Route es un backend FastAPI para la gestión de rutas de recolección de residuos sólidos, diseñado para operar en la ciudad de Buenaventura. El sistema soporta:

- **Autenticación y Autorización**: JWT con RBAC (Role-Based Access Control)
- **Gestión de Usuarios**: CRUD completo con roles (admin, driver, recolector, user)
- **Gestión de Vehículos**: Control de flota vehicular con estados operativos
- **Asignaciones de Rutas**: Asignación de vehículos a rutas externas con seguimiento
- **Tripulación**: Gestión de equipos de trabajo (piloto, copiloto, recolector)
- **Reportes**: Sistema de reportes operativos y públicos
- **WebSockets**: Comunicación en tiempo real para eventos de recorrido
- **Integración API Externa**: Consumo de APIs externas para rutas y recorridos

### 1.1 Tecnologías

| Componente    | Tecnología                      |
| ------------- | ------------------------------- |
| Framework     | FastAPI                         |
| Base de datos | PostgreSQL (async with asyncpg) |
| ORM           | SQLAlchemy (AsyncSession)       |
| Autenticación | JWT (PyJWT)                     |
| Validación    | Pydantic v2                     |
| Seguridad     | Bcrypt (passlib)                |

---

## 2. Arquitectura del Sistema

### 2.1 Capas de la Aplicación

```
┌─────────────────────────────────────────┐
│           ROUTERS (Rutas)               │
│   Definición de endpoints HTTP         │
├─────────────────────────────────────────┤
│         CONTROLLERS (Lógica)            │
│   Coordinación de dependencias         │
├─────────────────────────────────────────┤
│          SERVICES (Negocio)            │
│   Reglas de negocio y lógica           │
├─────────────────────────────────────────┤
│        MODELS (ORM/SQLAlchemy)         │
│   Mapeo a tablas de base de datos      │
├─────────────────────────────────────────┤
│       SCHEMAS (Pydantic)               │
│   Validación de datos y serialización  │
└─────────────────────────────────────────┘
```

### 2.2 Flujo de una Petición HTTP

1. **Cliente** envía request a un endpoint
2. **Router** decide el path y aplica `Depends` (autorización, body parsing)
3. **Controller** valida contexto y delega al Service
4. **Service** ejecuta reglas de negocio con SQLAlchemy asíncrono
5. **Model** interactúa con la base de datos
6. **Schema** valida y serializa la respuesta

### 2.3 Roles de Usuario

| Rol          | Descripción               | Permisos                                    |
| ------------ | ------------------------- | ------------------------------------------- |
| `admin`      | Administrador del sistema | Acceso completo a todas las funcionalidades |
| `driver`     | Conductor de vehículo     | Gestionar asignaciones y reportes de ruta   |
| `recolector` | Personal de recolección   | Visualización de asignaciones y reportes    |
| `user`       | Ciudadano/Usuario público | Acceso básico de consulta                   |

---

## 3. Módulos y Entidades

### 3.1 Estructura de Módulos

| Módulo            | Archivos Principales                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------- |
| **Usuarios**      | `model_usuarios.py`, `schema_usuarios.py`, `controller_usuarios.py`, `router_usuarios.py` |
| **Vehículos**     | `model_vehiculo.py`, `schema_vehiculo.py`, `controller_vehiculo.py`, `router_vehiculo.py` |
| **Rutas**         | `schema_rutas_externas.py`, `controller_rutas.py`, `router_rutas.py`                      |
| **Recorridos**    | `schema_recorridos_externos.py`, `controller_recorridos.py`, `router_recorridos.py`       |
| **Asignaciones**  | `model_asignacionrutas.py`, `schema_asignacionrutas.py`, `controller_asignacionrutas.py`  |
| **Tripulación**   | `model_tripulacion.py`, `model_asignaciontripulacion.py`, `schema_tripulacion.py`         |
| **Reportes**      | `model_reportes.py`, `schema_reportes.py`, `controller_reportes.py`                       |
| **Roles**         | `model_roles.py`, `schema_roles.py`, `controller_roles.py`                                |
| **Autenticación** | `model_auth.py`, `schema_auth.py`, `controller_auth.py`, `router_auth.py`                 |
| **Fotos**         | `model_fotos.py`, `schema_fotos.py`, `controller_fotos.py`, `router_fotos.py`             |

---

## 4. Endpoints REST API

### 4.1 Autenticación

| Método | Ruta                    | Descripción                          | Rol     |
| ------ | ----------------------- | ------------------------------------ | ------- |
| POST   | `/auth/login`           | Iniciar sesión con credenciales      | Público |
| POST   | `/auth/forgot-password` | Solicitar recuperación de contraseña | Público |
| POST   | `/auth/reset-password`  | Restablecer contraseña               | Público |

#### Parámetros - Login

- **Body (form-data)**:
  - `identifier`: string (username o correo electrónico)
  - `contraseña`: string (contraseña del usuario)

#### Respuesta - Login

```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
}
```

---

### 4.2 Roles (Admin)

| Método | Ruta           | Descripción                        | Rol   |
| ------ | -------------- | ---------------------------------- | ----- |
| GET    | `/admin/roles` | Listar todos los roles disponibles | admin |

#### Respuesta

```json
{
  "success": true,
  "message": "OK",
  "data": [
    {
      "id_rol": 1,
      "nombre": "admin",
      "descripcion": "Administrador del sistema"
    },
    {
      "id_rol": 2,
      "nombre": "driver",
      "descripcion": "Conductor de vehículo"
    }
  ]
}
```

---

### 4.3 Usuarios (Admin)

| Método | Ruta                           | Descripción                   | Rol   |
| ------ | ------------------------------ | ----------------------------- | ----- |
| GET    | `/admin/usuarios`              | Listar todos los usuarios     | admin |
| POST   | `/admin/usuarios`              | Crear nuevo usuario           | admin |
| GET    | `/admin/usuarios/{id_usuario}` | Obtener usuario por ID        | admin |
| PATCH  | `/admin/usuarios/{id_usuario}` | Actualizar usuario            | admin |
| DELETE | `/admin/usuarios/{id_usuario}` | Eliminar (desactivar) usuario | admin |

#### Parámetros - Crear Usuario

- **Body (JSON)**:

```json
{
  "nombre": "Juan Pérez",
  "username": "juanperez",
  "correo": "juan@ejemplo.com",
  "contraseña": "Password123!",
  "id_rol": 2,
  "activo": true
}
```

#### Restricciones:

- `username`: 3-50 caracteres, único
- `correo`: formato email válido, único
- `contraseña`: mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial
- `id_rol`: debe ser mayor a 0

#### Respuesta - Éxito (201 Created)

```json
{
  "success": true,
  "message": "Usuario creado exitosamente",
  "data": {
    "id_usuario": 10,
    "username": "juanperez",
    "correo": "juan@ejemplo.com",
    "activo": true,
    "id_perfil": 1,
    "id_rol": 2,
    "perfil": { ... },
    "rol": { ... },
    "created_at": "2026-04-23T10:30:00Z",
    "updated_at": "2026-04-23T10:30:00Z"
  }
}
```

#### Respuesta - Error (422 Validation Error)

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "El correo ya está registrado",
    "details": null,
    "path": "/admin/usuarios",
    "method": "POST",
    "timestamp": "2026-04-23T10:30:00Z"
  }
}
```

---

### 4.4 Vehículos (Admin)

| Método | Ruta                                    | Descripción                 | Rol   |
| ------ | --------------------------------------- | --------------------------- | ----- |
| GET    | `/admin/vehiculos`                      | Listar todos los vehículos  | admin |
| POST   | `/admin/vehiculos`                      | Crear nuevo vehículo        | admin |
| GET    | `/admin/vehiculos/{id_vehiculo}`        | Obtener vehículo por ID     | admin |
| PATCH  | `/admin/vehiculos/{id_vehiculo}`        | Actualizar vehículo         | admin |
| PATCH  | `/admin/vehiculos/{id_vehiculo}/estado` | Cambiar estado del vehículo | admin |
| DELETE | `/admin/vehiculos/{id_vehiculo}`        | Eliminar vehículo           | admin |

#### Parámetros - Crear Vehículo

- **Body (JSON)**:

```json
{
  "placa": "ABC123",
  "modelo": "Ford Cargo 1723",
  "capacidad_m3": 15.5,
  "estado": "disponible"
}
```

#### Restricciones:

- `placa`: formato `^[A-Z]{3}\d{3}$` (3 letras + 3 números), única
- `modelo`: máximo 50 caracteres
- `capacidad_m3`: debe ser mayor a 0
- `estado`: enum (`disponible`, `en_ruta`, `mantenimiento`, `inactivo`)

#### Estados de Vehículo

| Estado          | Descripción                         |
| --------------- | ----------------------------------- |
| `disponible`    | Vehículo disponible para asignación |
| `en_ruta`       | Vehículo actualmente en recorrido   |
| `mantenimiento` | Vehículo en mantenimiento           |
| `inactivo`      | Vehículo fuera de servicio          |

#### Respuesta - Éxito

```json
{
  "success": true,
  "message": "Vehículo creado exitosamente",
  "data": {
    "id_vehiculo": 5,
    "id_externo": null,
    "placa": "ABC123",
    "modelo": "Ford Cargo 1723",
    "capacidad_m3": 15.5,
    "estado": "disponible",
    "created_at": "2026-04-23T10:30:00Z"
  }
}
```

---

### 4.5 Rutas (Integración Externa)

| Método | Ruta              | Descripción                    | Rol   |
| ------ | ----------------- | ------------------------------ | ----- |
| GET    | `/api/rutas`      | Listar rutas desde API externa | admin |
| GET    | `/api/rutas/{id}` | Obtener ruta específica        | admin |
| POST   | `/api/rutas`      | Crear ruta en API externa      | admin |

#### Parámetros - Listar Rutas

- **Query**: `perfil_id` (opcional): UUID del perfil

#### Parámetros - Crear Ruta

- **Body (JSON)**:

```json
{
  "nombre_ruta": "Ruta Centro",
  "perfil_id": "550e8400-e29b-41d4-a716-446655440000",
  "calles_ids": ["550e8400-e29b-41d4-a716-446655440001"],
  "shape": null
}
```

#### Restricciones:

- Debe enviarse exactamente uno de: `calles_ids` o `shape`
- `nombre_ruta`: 1-255 caracteres

---

### 4.6 Recorridos (Integración Externa)

| Método | Ruta                                        | Descripción             | Rol    |
| ------ | ------------------------------------------- | ----------------------- | ------ |
| POST   | `/api/recorridos/iniciar`                   | Iniciar nuevo recorrido | driver |
| POST   | `/api/recorridos/{recorrido_id}/posiciones` | Registrar posición GPS  | driver |

#### Parámetros - Iniciar Recorrido

- **Body (JSON)**:

```json
{
  "ruta_id": "550e8400-e29b-41d4-a716-446655440000",
  "vehiculo_id": "550e8400-e29b-41d4-a716-446655440099"
}
```

#### Parámetros - Registrar Posición

- **Body (JSON)**:

```json
{
  "lat": 3.8801,
  "lon": -77.0188
}
```

---

### 4.7 Asignaciones (Admin)

| Método | Ruta                                           | Descripción                      | Rol   |
| ------ | ---------------------------------------------- | -------------------------------- | ----- |
| GET    | `/admin/asignaciones`                          | Listar todas las asignaciones    | admin |
| POST   | `/admin/asignaciones`                          | Crear nueva asignación           | admin |
| GET    | `/admin/asignaciones/{id_asignacion}`          | Obtener asignación por ID        | admin |
| GET    | `/admin/asignaciones/rutas/{id_ruta}`          | Obtener detalles de ruta externa | admin |
| POST   | `/admin/asignaciones/{id_asignacion}/cancelar` | Cancelar asignación              | admin |

#### Parámetros - Crear Asignación

- **Body (JSON)**:

```json
{
  "id_vehiculo": 5,
  "id_ruta": "ruta-externa-001",
  "id_tripulacion": 1,
  "fecha": "2026-04-23T10:00:00Z"
}
```

#### Estados de Asignación

| Estado       | Descripción                                  |
| ------------ | -------------------------------------------- |
| `pendiente`  | Asignación creada, await inicio de recorrido |
| `en_curso`   | Recorrido iniciado por el conductor          |
| `completada` | Recorrido finalizado exitosamente            |
| `cancelada`  | Asignación cancelada                         |

---

### 4.8 Asignaciones (Driver)

| Método | Ruta                                             | Descripción                  | Rol    |
| ------ | ------------------------------------------------ | ---------------------------- | ------ |
| GET    | `/driver/asignaciones/{id_asignacion}`           | Ver asignación del conductor | driver |
| POST   | `/driver/asignaciones/{id_asignacion}/iniciar`   | Iniciar recorrido            | driver |
| POST   | `/driver/asignaciones/{id_asignacion}/finalizar` | Finalizar recorrido          | driver |

#### Flujo del Conductor

1. **Ver asignación**: Consultar la asignación asignada al conductor
2. **Iniciar recorrido**: Cambia estado de `pendiente` → `en_curso`, registra `hora_salida`
3. **Finalizar recorrido**: Cambia estado de `en_curso` → `completada`

#### Restricciones:

- Solo puede haber **1 recorrido activo** por vehículo a la vez
- Duración máxima del recorrido: **24 horas**
- Al iniciar, se verifica que el vehículo no tenga otro recorrido activo

---

### 4.9 Tripulación (Admin)

| Método | Ruta                                                           | Descripción                      | Rol   |
| ------ | -------------------------------------------------------------- | -------------------------------- | ----- |
| POST   | `/admin/asignaciones/{id_asignacion}/tripulacion`              | Agregar miembro a tripulación    | admin |
| DELETE | `/admin/asignaciones/{id_asignacion}/tripulacion/{id_usuario}` | Eliminar miembro de tripulación  | admin |
| GET    | `/admin/asignaciones/{id_asignacion}/tripulacion`              | Listar tripulación de asignación | admin |
| GET    | `/admin/asignaciones/todas`                                    | Listar todas las tripulaciones   | admin |

#### Parámetros - Agregar Tripulación

- **Body (JSON)**:

```json
{
  "id_usuario": 10,
  "rol_tripulacion": "recolector"
}
```

#### Roles de Tripulación

| Rol          | Descripción                         |
| ------------ | ----------------------------------- |
| `piloto`     | Conductor principal del vehículo    |
| `copiloto`   | Ayudante de conductor               |
| `recolector` | Personal de recolección de residuos |

---

### 4.10 Tripulación (Driver)

| Método | Ruta                                               | Descripción              | Rol    |
| ------ | -------------------------------------------------- | ------------------------ | ------ |
| GET    | `/driver/asignaciones/{id_asignacion}/tripulacion` | Ver tripulación asignada | driver |
| POST   | `/driver/asignaciones/{id_asignacion}/confirmar`   | Confirmar participación  | driver |

---

### 4.11 Reportes (Admin)

| Método | Ruta                              | Descripción                        | Rol   |
| ------ | --------------------------------- | ---------------------------------- | ----- |
| GET    | `/admin/reportes`                 | Listar todos los reportes          | admin |
| GET    | `/admin/reportes/{id_reporte}`    | Obtener reporte por ID             | admin |
| PATCH  | `/admin/reportes/{id_reporte}/terminar` | Marcar reporte como terminado | admin |

#### Restricciones del Admin:

- **NO puede crear reportes** - Solo puede visualizar los reportes creados por los conductores
- **SOLO puede listar** todos los reportes del sistema
- **Puede marcar como terminado** los reportes para indicar que han sido atendidos

#### Parámetros - Marcar Reporte como Terminado

- **Body (JSON)**:

```json
{
  "notas_terminacion": "Problema solucionado, vehículo operativo"
}
```

#### Estados de Reportes

| Estado | Descripción                     |
| ------ | ------------------------------- |
| `baja` | Incidente menor, baja prioridad |
| `media`| Incidente moderado              |
| `alta` | Incidente crítico, alta prioridad|

### 4.12 Reportes (Driver)

| Método | Ruta                              | Descripción                          | Rol    |
| ------ | --------------------------------- | ------------------------------------ | ------ |
| GET    | `/driver/reportes`                 | Listar reportes del conductor        | driver |
| POST   | `/driver/reportes`                | Crear reporte con fotos              | driver |
| GET    | `/driver/reportes/{id_reporte}`    | Obtener reporte por ID               | driver |

#### Responsabilidades del Conductor:

- **ÚNICAMENTE puede crear reportes** - Es el único rol que puede generar reportes operativos
- **Adjuntar fotos como evidencia** - Las fotos sirven como prueba de lo que sucedió
- **Definir el nivel de prioridad** - Establece si el incidente es baja, media o alta prioridad
- **Notificación automática** - Al crear un reporte se notifica automáticamente al admin

#### Parámetros - Crear Reporte con Fotos

- **Body (JSON)**:

```json
{
  "asunto": "Problema mecánico",
  "descripcion": "El vehículo presenta fallos en el sistema de frenos",
  "estado": "alta",
  "fotos": [
    {
      "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "tipo": "evidencia",
      "timestamp": "2026-04-23T10:30:00Z"
    }
  ],
  "id_asignacion": 45
}
```

#### Restricciones:

- `asunto`: máximo 100 caracteres
- `descripcion`: requerido, máximo 1000 caracteres
- `estado`: Enum (`baja`, `media`, `alta`) - **Definido por el conductor según la gravedad**
- `fotos`: array opcional de fotos en base64 - **Sirven como evidencia del incidente**
- `id_asignacion`: ID de la asignación actual (opcional)

#### Flujo del Conductor:

1. **Crear reporte**: El conductor crea reportes durante su recorrido para documentar incidentes
2. **Adjuntar fotos**: Las fotos funcionan como prueba/evidencia de lo que ocurrió
3. **Establecer prioridad**: El conductor define la urgencia (baja, media, alta) según el impacto
4. **Notificación al admin**: Se envía automáticamente una notificación por WebSocket al admin

#### Respuesta - Éxito (201 Created)

```json
{
  "success": true,
  "message": "Reporte creado exitosamente",
  "data": {
    "id_registro": 150,
    "asunto": "Problema mecánico",
    "descripcion": "El vehículo presenta fallos en el sistema de frenos",
    "estado": "alta",
    "fecha": "2026-04-23T10:30:00Z",
    "id_usuario": 25,
    "id_asignacion": 45,
    "fotos": [
      {
        "id_foto": 200,
        "url": "/uploads/fotos/45_abc123def456.jpg",
        "tipo": "evidencia",
        "timestamp_captura": "2026-04-23T10:30:00Z"
      }
    ],
    "terminado": false,
    "notas_terminacion": null,
    "created_at": "2026-04-23T10:31:00Z"
  }
}
```

---

### 4.13 Reportes (Público)

| Método | Ruta        | Descripción                             | Rol     |
| ------ | ----------- | --------------------------------------- | ------- |
| POST   | `/reportes` | Crear reporte público sin autenticación | Público |

#### Parámetros - Crear Reporte Público

- **Body (JSON)**:

```json
{
  "nombre": "Ciudadano Ejemplo",
  "correo": "ciudadano@email.com",
  "descripcion": "No pasaron a recoger en mi barrio desde hace 3 días",
  "asunto": "Falta de recolección",
  "evidencia_url": "https://ejemplo.com/foto.jpg"
}
```

---

### 4.13 Rutas (Público - Ciudadano)

| Método | Ruta                       | Descripción                    | Rol  |
| ------ | -------------------------- | ------------------------------ | ---- |
| GET    | `/rutas/{id_ruta}/horario` | Ver horario de ruta específica | user |

#### Respuesta

```json
{
  "success": true,
  "message": "Horario de ruta obtenido exitosamente",
  "data": {
    "id_ruta": "ruta-externa-001",
    "id_vehiculo": 5,
    "hora_salida": "2026-04-23T06:00:00Z",
    "estado": "en_curso"
  }
}
```

---

### 4.14 Fotos (Driver)

| Método | Ruta                                             | Descripción                          | Rol    |
| ------ | ------------------------------------------------ | ------------------------------------ | ------ |
| POST   | `/driver/asignaciones/{id_asignacion}/fotos`      | Registrar foto/evidencia del recorrido | driver |
| GET    | `/driver/asignaciones/{id_asignacion}/fotos`      | Listar fotos de una asignación        | driver |

#### Parámetros - Registrar Foto

- **Body (JSON)**:

```json
{
  "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "tipo": "evidencia",
  "timestamp": "2026-04-23T10:30:00Z"
}
```

#### Restricciones:

- `imagen_base64`: Formato `data:image/<tipo>;base64,<datos>` (jpg, png, gif, webp)
- `tipo`: Enum (`evidencia`, `incidente`, `llegada`, `salida`, `completado`)
- `timestamp`: ISO 8601 datetime, timezone aware
- Solo se permite registrar fotos para asignaciones en estado `en_curso`

#### Tipos de Foto

| Tipo        | Descripción                           |
| ----------- | ------------------------------------- |
| `evidencia` | Evidencia general del recorrido        |
| `incidente`  | Incidente o problema durante ruta     |
| `llegada`   | Foto al llegar a destino             |
| `salida`     | Foto al iniciar el recorrido         |
| `completado` | Foto al finalizar el recorrido       |

#### Respuesta - Éxito (201 Created)

```json
{
  "success": true,
  "message": "Foto registrada exitosamente",
  "data": {
    "id_foto": 123,
    "id_asignacion": 45,
    "url": "/uploads/fotos/45_abc123def456.jpg",
    "tipo": "evidencia",
    "timestamp_captura": "2026-04-23T10:30:00Z",
    "created_at": "2026-04-23T10:31:00Z"
  }
}
```

#### Respuesta - Listar Fotos

```json
{
  "success": true,
  "message": "Fotos obtenidas exitosamente",
  "data": {
    "items": [
      {
        "id_foto": 123,
        "id_asignacion": 45,
        "url": "/uploads/fotos/45_abc123def456.jpg",
        "tipo": "evidencia",
        "timestamp_captura": "2026-04-23T10:30:00Z",
        "created_at": "2026-04-23T10:31:00Z"
      }
    ],
    "total": 1
  }
}
```

---

### 4.15 WebSockets

| Método | Ruta                                         | Descripción                        |
| ------ | -------------------------------------------- | ---------------------------------- |
| GET    | `/ws/stats`                                  | Obtener estadísticas de conexiones |
| WS     | `/ws/asignacion/{id_asignacion}?token={jwt}` | Conexión WebSocket para asignación |

---

## 5. Modelos de Datos

### 5.1 Usuario (`Usuario`)

| Campo        | Tipo        | Requerido | Restricciones                      |
| ------------ | ----------- | --------- | ---------------------------------- |
| `id_usuario` | Integer     | Sí        | Primary Key, Auto-increment        |
| `id_perfil`  | Integer     | Sí        | Foreign Key → `perfiles.id_perfil` |
| `id_rol`     | Integer     | Sí        | Foreign Key → `roles.id_rol`       |
| `username`   | String(50)  | Sí        | Único, index, 3-50 caracteres      |
| `correo`     | String(100) | Sí        | Único, index, formato email        |
| `contraseña` | String(255) | Sí        | Hash bcrypt                        |
| `activo`     | Boolean     | Sí        | Default `True`                     |
| `created_at` | DateTime    | Sí        | Timezone aware, auto               |
| `updated_at` | DateTime    | Sí        | Timezone aware, auto               |

#### Relaciones:

- `perfil` → `Perfil` (one-to-one)
- `rol` → `Rol` (many-to-one)
- `miembros_tripulacion` → `TripulacionMiembro` (one-to-many)
- `reportes_actividad` → `ReporteActividad` (one-to-many)

---

### 5.2 Vehículo (`Vehiculo`)

| Campo          | Tipo        | Requerido | Restricciones                        |
| -------------- | ----------- | --------- | ------------------------------------ |
| `id_vehiculo`  | Integer     | Sí        | Primary Key, Auto-increment          |
| `id_externo`   | String(36)  | No        | UUID único, para integración externa |
| `placa`        | String(20)  | Sí        | Único, formato `^[A-Z]{3}\d{3}$`     |
| `modelo`       | String(100) | No        | Máximo 100 caracteres                |
| `capacidad_m3` | Float       | No        | Mayor a 0                            |
| `estado`       | Enum        | Sí        | `EstadoVehiculo`                     |
| `created_at`   | DateTime    | Sí        | Timezone aware, auto                 |

#### Estados (`EstadoVehiculo`):

- `disponible`
- `en_ruta`
- `mantenimiento`
- `inactivo`

---

### 5.3 Asignación de Rutas (`AsignacionRutas`)

| Campo            | Tipo        | Requerido | Restricciones                                |
| ---------------- | ----------- | --------- | -------------------------------------------- |
| `id_asignacion`  | Integer     | Sí        | Primary Key, Auto-increment                  |
| `id_vehiculo`    | Integer     | Sí        | Foreign Key → `vehiculos.id_vehiculo`        |
| `id_ruta`        | String(100) | Sí        | ID externo de la API de rutas                |
| `id_tripulacion` | Integer     | No        | Foreign Key → `tripulaciones.id_tripulacion` |
| `hora_salida`    | DateTime    | No        | Se llena al iniciar recorrido                |
| `fecha`          | DateTime    | Sí        | Timezone aware                               |
| `estado`         | Enum        | Sí        | `EstadoAsignacion`, default `pendiente`      |
| `created_at`     | DateTime    | Sí        | Timezone aware, auto                         |

#### Estados (`EstadoAsignacion`):

- `pendiente`
- `en_curso`
- `completada`
- `cancelada`

---

### 5.4 Tripulación (`Tripulacion`)

| Campo            | Tipo        | Requerido | Restricciones               |
| ---------------- | ----------- | --------- | --------------------------- |
| `id_tripulacion` | Integer     | Sí        | Primary Key, Auto-increment |
| `nombre`         | String(100) | No        | Nombre de la tripulación    |
| `created_at`     | DateTime    | Sí        | Timezone aware, auto        |

#### Relaciones:

- `miembros` → `TripulacionMiembro` (one-to-many, cascade delete)
- `asignaciones` → `AsignacionRutas` (one-to-many)

---

### 5.5 Miembro de Tripulación (`TripulacionMiembro`)

| Campo             | Tipo     | Requerido | Restricciones                                |
| ----------------- | -------- | --------- | -------------------------------------------- |
| `id`              | Integer  | Sí        | Primary Key, Auto-increment                  |
| `id_tripulacion`  | Integer  | Sí        | Foreign Key → `tripulaciones.id_tripulacion` |
| `id_usuario`      | Integer  | Sí        | Foreign Key → `usuarios.id_usuario`          |
| `rol_tripulacion` | Enum     | Sí        | `RolTripulacion`                             |
| `confirmado`      | Boolean  | Sí        | Default `False`                              |
| `confirmado_at`   | DateTime | No        | Timezone aware                               |

#### Roles de Tripulación (`RolTripulacion`):

- `piloto`
- `copiloto`
- `recolector`

---

### 5.6 Reporte de Actividad (`ReporteActividad`)

| Campo               | Tipo        | Requerido | Restricciones                                |
| ------------------- | ----------- | --------- | -------------------------------------------- |
| `id_registro`       | BigInteger  | Sí        | Primary Key                                  |
| `id_usuario`        | Integer     | Sí        | Foreign Key → `usuarios.id_usuario`          |
| `id_asignacion`     | Integer     | No        | Foreign Key → `asignaciones_rutas.id_asignacion` |
| `asunto`            | String(100) | Sí        | Asunto del reporte                          |
| `descripcion`       | Text        | Sí        | Descripción del reporte                      |
| `estado`            | Enum        | Sí        | `EstadoReporte` (baja, media, alta)         |
| `fecha`             | DateTime    | Sí        | Timezone aware, auto                        |
| `terminado`         | Boolean     | Sí        | Default `False`                              |
| `notas_terminacion` | Text        | No        | Notas al marcar como terminado               |
| `fecha_terminacion` | DateTime    | No        | Fecha en que se marcó como terminado         |
| `created_at`        | DateTime    | Sí        | Timezone aware, auto                        |
| `updated_at`        | DateTime    | Sí        | Timezone aware, auto                        |

#### Estados de Reporte (`EstadoReporte`):

- `baja` - Incidente menor, baja prioridad
- `media` - Incidente moderado, prioridad media
- `alta` - Incidente crítico, alta prioridad

#### Relaciones:

- `usuario` → `Usuario` (many-to-one)
- `asignacion` → `AsignacionRutas` (many-to-one, opcional)
- `fotos` → `RecorridoFoto` (one-to-many, a través de relación)

---

### 5.7 Foto del Recorrido (`RecorridoFoto`)

| Campo              | Tipo        | Requerido | Restricciones                                |
| ------------------ | ----------- | --------- | -------------------------------------------- |
| `id_foto`          | Integer     | Sí        | Primary Key, Auto-increment                  |
| `id_asignacion`    | Integer     | Sí        | Foreign Key → `asignaciones_rutas.id_asignacion` |
| `url`              | String(255) | Sí        | URL de acceso a la imagen almacenada         |
| `tipo`             | Enum        | Sí        | `TipoFoto`                                  |
| `timestamp_captura`| DateTime    | Sí        | Timezone aware, momento de captura de la foto |
| `created_at`       | DateTime    | Sí        | Timezone aware, auto                         |

#### Tipos de Foto (`TipoFoto`):

- `evidencia` - Evidencia general del recorrido
- `incidente` - Incidente o problema durante la ruta
- `llegada` - Foto al llegar al destino
- `salida` - Foto al iniciar el recorrido
- `completado` - Foto al finalizar el recorrido

#### Relaciones:

- `asignacion` → `AsignacionRutas` (many-to-one)

---

## 6. Esquemas Pydantic

### 6.1 Estructura de Respuesta Uniforme

#### SuccessResponse

```python
class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: T
```

#### ErrorResponse

```python
class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetailPayload

class ErrorDetailPayload(BaseModel):
    code: str          # Código de error (unauthorized, forbidden, not_found, etc.)
    message: str      # Mensaje descriptivo
    details: Any      # Detalles adicionales
    path: str         # Ruta del endpoint
    method: str       # Método HTTP
    timestamp: str    # Fecha/hora del error
```

---

### 6.2 Esquemas de Autenticación

| Schema          | Descripción                  |
| --------------- | ---------------------------- |
| `LoginRequest`  | `identifier`, `contraseña`   |
| `TokenResponse` | `access_token`, `token_type` |

---

### 6.3 Esquemas de Usuarios

| Schema                | Descripción                            |
| --------------------- | -------------------------------------- |
| `UsuarioAdminCreate`  | Para crear usuarios con rol específico |
| `UsuarioPublicCreate` | Registro público con rol `user`        |
| `UsuarioUpdate`       | Campos opcionales para actualización   |
| `UsuarioResponse`     | Respuesta completa con relaciones      |

---

### 6.4 Esquemas de Vehículos

| Schema             | Descripción                                   |
| ------------------ | --------------------------------------------- |
| `VehiculoCreate`   | `placa`, `modelo?`, `capacidad_m3?`, `estado` |
| `VehiculoUpdate`   | Campos opcionales                             |
| `VehiculoResponse` | Respuesta completa                            |

---

### 6.5 Esquemas de Asignaciones

| Schema                     | Descripción                                         |
| -------------------------- | --------------------------------------------------- |
| `AsignacionCreate`         | `id_vehiculo`, `id_ruta`, `id_tripulacion`, `fecha` |
| `AsignacionUpdate`         | `estado?`, `hora_salida?`                           |
| `AsignacionResponse`       | Respuesta con vehículo y tripulación                |
| `AsignacionPublicResponse` | Versión pública para ciudadanos                     |

---

### 6.6 Esquemas de Reportes

| Schema                     | Descripción                                    |
| -------------------------- | ---------------------------------------------- |
| `ReporteDriverCreate`      | `asunto`, `descripcion`, `estado`, `fotos?`, `id_asignacion?` |
| `ReporteAdminResponse`     | Respuesta completa con fotos y relaciones      |
| `ReporteDriverResponse`    | Versión para conductores                       |
| `ReporteTerminadoUpdate`   | `notas_terminacion` para marcar como terminado |
| `ReportePublicCreate`      | Para reportes públicos sin autenticación       |

---

### 6.7 Esquemas de Fotos

| Schema              | Descripción                                    |
| ------------------- | ---------------------------------------------- |
| `FotoCreate`        | `imagen_base64`, `tipo`, `timestamp`           |
| `FotoResponse`      | Respuesta completa con datos de la foto        |
| `FotoListResponse`  | Lista paginada de fotos con contador total       |

---

## 7. Ejemplos de Peticiones y Respuestas

### 7.1 Login Exitoso

#### Request

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "identifier=admin&contraseña=Admin123!"
```

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sIjoiYWRtaW4iLCJpYXQiOjE3MjQwNjU2MDB9.abc123xyz",
    "token_type": "bearer"
  }
}
```

### 7.2 Login Fallido

#### Request

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "identifier=admin&contraseña=wrongpassword"
```

#### Response (401 Unauthorized)

```json
{
  "success": false,
  "error": {
    "code": "unauthorized",
    "message": "Credenciales inválidas",
    "details": null,
    "path": "/auth/login",
    "method": "POST",
    "timestamp": "2026-04-23T10:30:00Z"
  }
}
```

### 7.3 Crear Usuario (Admin)

#### Request

```bash
curl -X POST "http://localhost:8000/admin/usuarios" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Carlos López",
    "username": "carloslopez",
    "correo": "carlos@empresa.com",
    "contraseña": "Pass1234!",
    "id_rol": 2,
    "activo": true
  }'
```

#### Response (201 Created)

```json
{
  "success": true,
  "message": "Usuario creado exitosamente",
  "data": {
    "id_usuario": 15,
    "username": "carloslopez",
    "correo": "carlos@empresa.com",
    "activo": true,
    "id_perfil": 1,
    "id_rol": 2,
    "perfil": {
      "id_perfil": 1,
      "nombre": "Usuario"
    },
    "rol": {
      "id_rol": 2,
      "nombre": "driver",
      "descripcion": "Conductor de vehículo"
    },
    "created_at": "2026-04-23T10:30:00Z",
    "updated_at": "2026-04-23T10:30:00Z"
  }
}
```

### 7.4 Iniciar Recorrido (Driver)

#### Request

```bash
curl -X POST "http://localhost:8000/driver/asignaciones/1/iniciar" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Recorrido iniciado exitosamente",
  "data": {
    "id_asignacion": 1,
    "id_vehiculo": 5,
    "id_ruta": "ruta-externa-001",
    "id_tripulacion": 1,
    "fecha": "2026-04-23T00:00:00Z",
    "hora_salida": "2026-04-23T06:15:00Z",
    "estado": "en_curso",
    "created_at": "2026-04-23T06:00:00Z",
    "vehiculo": {
      "id_vehiculo": 5,
      "placa": "ABC123",
      "modelo": "Ford Cargo",
      "estado": "en_ruta"
    },
    "tripulacion": {
      "id_tripulacion": 1,
      "nombre": "Equipo Mañana A",
      "miembros": [...]
    }
  }
}
```

### 7.5 Error de Validación

#### Request

```bash
curl -X POST "http://localhost:8000/admin/vehiculos" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"placa": "INVALID", "modelo": "Test"}'
```

#### Response (422 Unprocessable Entity)

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "1 validation error for VehiculoCreate\nplaca\n  String should match pattern '^[A-Z]{3}\\d{3}$'",
    "details": null,
    "path": "/admin/vehiculos",
    "method": "POST",
    "timestamp": "2026-04-23T10:30:00Z"
  }
}
```

### 7.6 Reporte Público

#### Request

```bash
curl -X POST "http://localhost:8000/reportes" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Ciudad",
    "correo": "juan@email.com",
    "descripcion": "No pasaron a recoger esta semana",
    "asunto": "Falta de servicio",
    "evidencia_url": "https://ejemplo.com/img.jpg"
  }'
```

#### Response (201 Created)

```json
{
  "success": true,
  "message": "Reporte creado exitosamente",
  "data": {
    "id_registro": 100,
    "nombre": "Juan Ciudad",
    "correo": "juan@email.com",
    "descripcion": "No pasaron a recoger esta semana",
    "asunto": "Falta de servicio",
    "evidencia_url": "https://ejemplo.com/img.jpg",
    "fecha": "2026-04-23T10:30:00Z"
  }
}
```

### 7.7 Crear Reporte con Fotos (Driver)

#### Request

```bash
curl -X POST "http://localhost:8000/driver/reportes" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "asunto": "Problema mecánico en frenos",
    "descripcion": "Los frenos no responden adecuadamente, es peligroso continuar",
    "estado": "alta",
    "id_asignacion": 45,
    "fotos": [
      {
        "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
        "tipo": "evidencia",
        "timestamp": "2026-04-23T10:30:00Z"
      },
      {
        "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQBBB...",
        "tipo": "incidente",
        "timestamp": "2026-04-23T10:31:00Z"
      }
    ]
  }'
```

#### Response (201 Created)

```json
{
  "success": true,
  "message": "Reporte creado exitosamente",
  "data": {
    "id_registro": 150,
    "asunto": "Problema mecánico en frenos",
    "descripcion": "Los frenos no responden adecuadamente, es peligroso continuar",
    "estado": "alta",
    "fecha": "2026-04-23T10:30:00Z",
    "id_usuario": 25,
    "id_asignacion": 45,
    "terminado": false,
    "notas_terminacion": null,
    "fotos": [
      {
        "id_foto": 200,
        "url": "/uploads/fotos/45_abc123def456.jpg",
        "tipo": "evidencia",
        "timestamp_captura": "2026-04-23T10:30:00Z"
      },
      {
        "id_foto": 201,
        "url": "/uploads/fotos/45_def789ghi012.jpg",
        "tipo": "incidente",
        "timestamp_captura": "2026-04-23T10:31:00Z"
      }
    ],
    "created_at": "2026-04-23T10:32:00Z",
    "updated_at": "2026-04-23T10:32:00Z"
  }
}
```

### 7.8 Marcar Reporte como Terminado (Admin)

#### Request

```bash
curl -X PATCH "http://localhost:8000/admin/reportes/150/terminar" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "notas_terminacion": "Mecánico revisó y reemplazó pastillas de freno. Vehículo operativo."
  }'
```

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Reporte marcado como terminado exitosamente",
  "data": {
    "id_registro": 150,
    "asunto": "Problema mecánico en frenos",
    "descripcion": "Los frenos no responden adecuadamente, es peligroso continuar",
    "estado": "alta",
    "fecha": "2026-04-23T10:30:00Z",
    "id_usuario": 25,
    "id_asignacion": 45,
    "terminado": true,
    "notas_terminacion": "Mecánico revisó y reemplazó pastillas de freno. Vehículo operativo.",
    "fecha_terminacion": "2026-04-23T14:15:00Z",
    "fotos": [
      {
        "id_foto": 200,
        "url": "/uploads/fotos/45_abc123def456.jpg",
        "tipo": "evidencia",
        "timestamp_captura": "2026-04-23T10:30:00Z"
      },
      {
        "id_foto": 201,
        "url": "/uploads/fotos/45_def789ghi012.jpg",
        "tipo": "incidente",
        "timestamp_captura": "2026-04-23T10:31:00Z"
      }
    ],
    "created_at": "2026-04-23T10:32:00Z",
    "updated_at": "2026-04-23T14:15:00Z"
  }
}
```

---

## 8. Funcionalidades Críticas

### 8.1 Geolocalización en Tiempo Real

| Funcionalidad                | Estado             | Descripción                                          |
| ---------------------------- | ------------------ | ---------------------------------------------------- |
| Registro de posiciones       | ✅ Implementado    | Endpoint `/api/recorridos/{recorrido_id}/posiciones` |
| Almacenamiento de posiciones | ⚠️ Parcial         | Se envía a API externa, no se almacena localmente    |
| Historial de ubicaciones     | ❌ No implementado | No hay tabla local para storing positions            |

#### Consideraciones:

- Las posiciones se registran contra la API externa
- No se mantiene historial local de posiciones
- **Recomendación**: Crear tabla `recorrido_posiciones` para almacenar historial

---

### 8.2 Envío de Fotografías en Base64

| Funcionalidad       | Estado             | Descripción                                     |
| ------------------- | ------------------ | ----------------------------------------------- |
| Campo evidencia_url | ✅ Implementado    | Almacena URL de evidencia en reportes           |
| Envío de Base64     | ❌ No implementado | No hay endpoint para recibir imágenes en Base64 |

#### Consideraciones:

- Actualmente solo se acepta URL (`evidencia_url`)
- **Recomendación**: Agregar endpoint `/api/upload` para recibir imágenes Base64 y almacenarlas en cloud/storage

---

### 8.3 Almacenamiento Local y Sincronización

| Funcionalidad            | Estado             | Descripción                         |
| ------------------------ | ------------------ | ----------------------------------- |
| Base de datos PostgreSQL | ✅ Implementado    | Almacenamiento principal            |
| Sincronización offline   | ❌ No implementado | No hay lógica de sincronización     |
| Cache local              | ⚠️ Parcial         | Cache en memoria para APIs externas |

#### Consideraciones:

- No hay soporte para modo offline
- **Recomendación**: Implementar lógica de sync para dispositivos móviles

---

### 8.4 Gestión de Recorridos

| Restricción                | Estado          | Descripción                        |
| -------------------------- | --------------- | ---------------------------------- |
| Solo 1 activo por vehículo | ✅ Implementado | Validación en `iniciar_recorrido`  |
| Máximo 24 horas            | ⚠️ Parcial      | No hay validación de tiempo máximo |
| Estado único               | ✅ Implementado | Enum `EstadoAsignacion`            |

#### Lógica implementada en `service_asignacionrutas.py`:

```python
# Verificar que el vehículo no tenga otro recorrido activo
vehiculo_en_ruta = await self.verificar_vehiculo_disponible(id_vehiculo)
if vehiculo_en_ruta:
    raise HTTPException(status_code=400, detail="El vehículo ya tiene un recorrido activo")
```

---

### 8.5 Historial de Hitos y Ubicaciones

| Funcionalidad            | Estado             | Descripción                                          |
| ------------------------ | ------------------ | ---------------------------------------------------- |
| Hitos de asignación      | ✅ Implementado    | Estados: pendiente → en_curso → completada/cancelada |
| Historial de cambios     | ❌ No implementado | No hay tabla de auditoría                            |
| Ubicaciones del vehículo | ⚠️ Parcial         | Solo se registra al iniciar/finalizar                |

#### Consideraciones:

- Solo se registra `hora_salida` al iniciar y estado al completar
- **Recomendación**: Crear tabla `asignacion_historial` para tracking de cambios

---

## 9. Estado de Implementación

### 9.1 Resumen de Módulos

| Módulo                 | CRUD Completo | Endpoints | Modelos | Schemas | Tests |
| ---------------------- | ------------- | --------- | ------- | ------- | ----- |
| **Autenticación**      | ✅            | 3         | 1       | 2       | ✅    |
| **Usuarios**           | ✅            | 5         | 1       | 4       | ✅    |
| **Vehículos**          | ✅            | 6         | 1       | 3       | ✅    |
| **Roles**              | ✅            | 1         | 1       | 1       | ✅    |
| **Asignaciones**       | ✅            | 10        | 1       | 4       | ✅    |
| **Tripulación**        | ✅            | 6         | 2       | 2       | ✅    |
| **Rutas (Ext)**        | ✅            | 3         | 0       | 3       | ❌    |
| **Recorridos (Ext)**   | ✅            | 2         | 0       | 3       | ❌    |
| **Reportes (Admin)**   | ✅            | 2         | 1       | 2       | ✅    |
| **Reportes (Público)** | ✅            | 1         | 1       | 2       | ✅    |
| **Fotos**             | ✅            | 2         | 1       | 3       | ❌    |
| **WebSockets**         | ✅            | 2         | 1       | 0       | ✅    |

### 9.2 Funcionalidades Implementadas vs Faltantes

| Funcionalidad                          | Implementado | Falta                  |
| -------------------------------------- | ------------ | ---------------------- |
| Autenticación JWT                      | ✅           | -                      |
| RBAC (roles)                           | ✅           | -                      |
| CRUD Usuarios                          | ✅           | -                      |
| CRUD Vehículos                         | ✅           | -                      |
| CRUD Asignaciones                      | ✅           | -                      |
| Gestión Tripulación                    | ✅           | -                      |
| Reportes Admin                         | ✅           | -                      |
| Reportes Públicos                      | ✅           | -                      |
| Fotos Base64                           | ✅           | -                      |
| WebSockets                             | ✅           | -                      |
| Integración API Rutas                  | ✅           | -                      |
| Integración API Recorridos             | ✅           | -                      |
| Geolocalización (envío)                | ✅           | -                      |
| Geolocalización (almacenamiento local) | ❌           | Tabla posiciones       |
| Sincronización offline                 | ❌           | Lógica sync            |
| Historial de hitos                     | ❌           | Tabla auditoría        |
| Duración máx. 24h recorrido            | ❌           | Validación             |
| Rate limiting                          | ⚠️ Parcial   | Configuración completa |
| Refresh tokens                         | ❌           | Implementar            |

---

## 10. WebSockets

### 10.1 Conexión

```
WebSocket: ws://<host>/ws/asignacion/{id_asignacion}?token=<JWT>
```

### 10.2 Autenticación

- Se requiere JWT válido en query parameter `token`
- El token se valida con `verificar_token` antes de aceptar la conexión
- Si el token es inválido, se cierra con código 1008 (policy violation)

### 10.3 Eventos

| Evento                 | Descripción                                     |
| ---------------------- | ----------------------------------------------- |
| `recorrido_iniciado`   | Envío cuando el conductor inicia el recorrido   |
| `recorrido_finalizado` | Envío cuando el conductor finaliza el recorrido |
| `asignacion_cancelada` | Envío cuando una asignación es cancelada        |

### 10.4 Estadísticas

```
GET /ws/stats
```

Respuesta:

```json
{
  "conexiones_activas": 5,
  "asignaciones_conectadas": [1, 3, 5, 7, 9]
}
```

---

## 11. Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Seguridad
SECRET_KEY=clave_secreta_generada
JWT_SECRET=clave_jwt_generada
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480

# CORS
CORS_ORIGINS=http://localhost:4200,http://localhost:3000

# API Externa de Rutas
RUTAS_API_URL=http://localhost:8001
```

---

## 12. Comandos de Ejecución

```bash
# Desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Tests
pytest -q

# Documentación Swagger
# http://localhost:8000/docs

# Documentación ReDoc
# http://localhost:8000/redoc
```

---

## 13. Contacto y Soporte

- **Desarrolladores:** Jose Luis Prado Valencia, Heiner Jair Godoy Zamora
- **Versión actual:** 1.0.2
- **Documentación interactiva:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
