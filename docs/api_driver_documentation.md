# Documentación de la API - Rol DRIVER

Esta documentación detalla de forma exclusiva la superficie de la API REST y WebSockets disponible para el rol `DRIVER` (Conductor) en el backend (FastAPI).

---

## 1. Arquitectura de Seguridad y RBAC (Control de Acceso)

Para garantizar la seguridad de los endpoints del conductor, el backend implementa el siguiente stack de protección:

- **Autenticación (JWT):** Todas las solicitudes (excepto rutas públicas específicas) requieren un token JWT válido enviado en el header `Authorization: Bearer <token>`. La validez se verifica a través del método `verificar_token` y el middleware/dependencia `HTTPBearer`.
- **Identificación del Usuario:** El decorador `get_current_user` inyectado por FastAPI resuelve y carga desde la base de datos al usuario asociado al token `sub`.
- **Autorización y Roles (Guards / Policies):** Se restringe el acceso utilizando la dependencia dedicada `DriverDep`, la cual ejecuta la función `require_rol(TipoRol.driver)`. Solo los usuarios con el rol oficial de `DRIVER` pueden consumir estas rutas; de lo contrario, se lanza una excepción `403 Forbidden`.
- **Módulos relacionados:** 
  - `core/dependecies.py`: Contiene los guards (`DriverDep`, `get_current_user`, `require_rol`).
  - `core/security.py`: Verificación y validación de tokens JWT.
  - `routers/router_*.py`: Archivos donde se aplican las restricciones en los `APIRouter`.

---

## 2. Endpoints Permitidos para DRIVER

Los endpoints están estandarizados para devolver un wrapper genérico `SuccessResponse[T]`.

### A. Asignaciones de Rutas (Recorridos)
**Router:** `router_asignacionrutas.py` | **Prefijo base:** `/driver/asignaciones`

| Método | Endpoint | Descripción | Body / Query | Respuesta |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista todas las asignaciones del conductor logueado. | - | `200 OK` (Array `AsignacionResponse`) |
| `GET` | `/{id_asignacion}` | Ver los detalles y el estado de una asignación específica. | - | `200 OK` (`AsignacionResponse`) |
| `POST` | `/{id_asignacion}/iniciar` | Inicia el recorrido de la asignación. | - | `200 OK` (`AsignacionResponse`) |
| `POST` | `/{id_asignacion}/finalizar` | Finaliza la recolección y termina el recorrido. | - | `200 OK` (`AsignacionResponse`) |

---

### B. Tripulación (Miembros del Equipo)
**Router:** `router_asignaciontripulacion.py` | **Prefijo base:** `/driver/asignaciones`

| Método | Endpoint | Descripción | Body / Query | Respuesta |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/{id_asignacion}/tripulacion` | Consulta la lista de recolectores/ayudantes asignados a la ruta. | - | `200 OK` (Array `TripulacionResponse`) |
| `POST` | `/{id_asignacion}/confirmar` | Confirma la participación del conductor en dicha ruta. | - | `200 OK` (`TripulacionResponse`) |

---

### C. Posiciones (GPS / Monitoreo en Vivo)
**Router:** `router_posiciones.py` | **Prefijo base:** `/driver/asignaciones`

| Método | Endpoint | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `POST` | `/{id_asignacion}/posiciones` | Registra en la DB una coordenada GPS capturada durante el viaje. | `201 Created` (`PosicionResponse`) |

**Body de Ejemplo (`PosicionCreate`):**
```json
{
  "latitud": 3.8801,
  "longitud": -77.0188,
  "accuracy": 5.2,
  "speed": 25.3,
  "bearing": 45.5,
  "timestamp": "2026-04-23T10:30:00Z"
}
```

#### Nueva funcionalidad: Envío de posición a API externa de recorridos
Además del guardado local en DB, el conductor ahora puede reportar posiciones directamente al servicio externo de recorridos.

**Router:** `router_recorridos.py` | **Prefijo base:** `/recorridos`

| Método | Endpoint | Descripción | Seguridad | Respuesta |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/{recorrido_id}/posiciones` | Registra una posición GPS para un recorrido externo activo. | `DriverDep` (solo rol `DRIVER`) | `201 Created` (`RecorridoResponse`) |

**Body de Ejemplo (`RegistrarPosicionRequest`):**
```json
{
  "lat": 3.42155,
  "lon": -76.5205,
  "perfil_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

**Notas importantes:**
- `perfil_id` es opcional en el body: si no se envía, el backend usa `PERFIL_ID` de configuración.
- Este endpoint usa `recorrido_id` (UUID del recorrido externo), no `id_asignacion` local.
- Errores esperados: `403` (sin permisos), `422` (validación), `502` (fallo de conexión con API externa).

#### Consulta de posiciones del recorrido externo (contexto operativo)
Este endpoint no es exclusivo del conductor, pero se documenta aquí porque complementa el flujo de rastreo:

| Método | Endpoint | Descripción | Seguridad | Respuesta |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/{recorrido_id}/posiciones` | Lista historial de posiciones del recorrido externo. | Público (sin login) y accesible por admin | `200 OK` |

**Query params:**
- `perfil_id` (opcional): perfil propietario para validación de permisos en API externa.

---

### D. Fotos (Evidencia Visual)
**Router:** `router_fotos.py` | **Prefijo base:** `/driver/asignaciones`

| Método | Endpoint | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `POST` | `/{id_asignacion}/fotos` | Sube una foto (en Base64) como evidencia de recolección, cumplimiento o incidencias. | `201 Created` (`FotoResponse`) |

**Body de Ejemplo (`FotoCreate`):**
```json
{
  "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSk...",
  "timestamp": "2026-04-23T10:30:00Z",
  "tipo": "recoleccion" // Valores: recoleccion | incidencia | cumplimiento
}
```

---

### E. Reportes de Incidencias
**Router:** `router_driver_reportes.py` | **Prefijo base:** `/driver/reportes`

| Método | Endpoint | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista el historial de reportes creados por el conductor. | `200 OK` (Array `ReporteDriverResponse`) |
| `GET` | `/{id_reporte}` | Detalles completos de un reporte específico. | `200 OK` (`ReporteDriverResponse`) |
| `POST` | `/` | Abre un nuevo ticket o reporte de incidencia en vía. | `201 Created` (`ReporteDriverResponse`) |

**Body de Ejemplo (`ReporteDriverCreate`):**
```json
{
  "asunto": "Falla mecánica en camión",
  "descripcion": "El camión no enciende después de la recolección en calle 5.",
  "estado": "alta", // Valores: baja, media, alta
  "id_asignacion": 15
}
```

---

### F. WebSockets (Comunicación Bidireccional)
**Router:** `router_ws.py` | **Prefijo base:** `/asignacion`

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `WS` | `/{id_asignacion}?token=<jwt_token>` | Conexión a WebSocket para enviar ping de presencia y notificar actualizaciones de estado en tiempo real. |

**Flujo de Envío de Mensaje por WebSocket:**
El conductor puede emitir eventos como cambios de estado (`status_update`) para informar al instante a los administradores. Esta conexión valida permisos con `AsignacionService.verificar_permiso_usuario`.

**Payload de ejemplo emitido por el cliente:**
```json
{
  "type": "status_update",
  "id": "msg-98765",
  "estado": "en_curso",
  "estado_anterior": "pendiente"
}
```
