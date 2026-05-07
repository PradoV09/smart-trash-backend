# 🚛 Smart Trash Routes – Backend (FastAPI)

![Version](https://img.shields.io/badge/version-1.0.3-blue)
![Tests](https://img.shields.io/badge/tests-8%20passed-green)
![Python](https://img.shields.io/badge/python-3.13.13-blue)

> ⚠️ **Versión 1.0.3** – MVP Backend funcional con **FastAPI (Python)**.
> Simplificado para MVP: solo Admin y Driver tienen funcionalidades activas.

> API del sistema web para gestionar y visualizar rutas de camiones de basura en Buenaventura 🌍
> **Backend desarrollado por: _Heiner jair godoy zamora y Jose luis prado valencia_**

---
## 🧠 Contexto del Problema

En Buenaventura no hay claridad sobre los horarios ni los recorridos de los camiones de basura. Esto genera:

- 🗑️ Acumulación de residuos
- 😷 Malos olores
- 🚯 Desorden en las calles

El backend de este proyecto se encarga de manejar toda la lógica, datos y validaciones necesarias para soportar la solución.

---
## 🎯 Objetivo del Backend

Este servidor implementado en **FastAPI** tiene como propósito:

- 🧍‍♂️ Gestionar **camiones y empleados (CRUD completo)**
- 🚚 Manejar **rutas y posiciones geográficas**
- 🛰️ Proveer endpoints para **simulación de recorridos en tiempo real**
- 🔐 Administrar seguridad JWT con **autorización por roles (RBAC)**
- 🗺️ Servir datos geoespaciales desde **PostgreSQL + PostGIS**
- ⚡ Estar **optimizado con programación asíncrona (`async`/`await`)** para mejorar rendimiento y concurrencia
- 🌐 **Listo para consumir APIs externas** (configurado para integración)
- 📖 Documentación automática completa con **Swagger UI y ReDoc**

---
## 🚀 Estado Actual del Proyecto

### ✅ **Funcionalidades Implementadas:**

- **Autenticación JWT** con roles (admin, driver, recolector)
- **WebSockets operativos** para comunicación en tiempo real con ping/pong keepalive
- **CRUD completo** de usuarios (solo admin), vehículos, asignaciones
- **Reportes Públicos** - Ciudadanos pueden reportar problemas sin registro
- **Base de datos PostgreSQL** con migraciones Alembic
- **API externa integrada** para validación de rutas
- **Tests automatizados** (8/8 pasan correctamente)
- **Documentación completa** y ejemplos de integración

### 🎭 **Roles del MVP:**

| Rol | Funciones |
|-----|-----------|
| **Admin** | Crea usuarios (admin/driver/recolector), gestiona asignaciones y tripulación |
| **Driver** | Confirma participación, inicia/finaliza recorridos, consulta asignación y tripulación |
| **Recolector** | Rol pasivo - solo existe como entidad para ser asignado a tripulación (sin endpoints propios) |
| **User** | ❌ Eliminado del MVP - no hay registro público |
| **Ciudadano** | ✅ Puede ver rutas públicas y crear reportes sin autenticación |

### ⚡ **Optimizaciones Realizadas:**

- **Configuración .env segura** con JWT_SECRET generado correctamente
- **WebSockets optimizados** con manejo robusto de conexiones
- **Gestión de dependencias** y CORS configurado para múltiples orígenes
- **Eliminación de tags duplicados** en Swagger UI

### 🔧 **Correcciones de Errores:**

- **Sintaxis en archivos de documentación** - Convertidos a comentarios puros
- **Configuración de routers** - Eliminación de prefijos duplicados
- **Variables de entorno** - JWT_SECRET seguro y RUTAS_API_URL agregado
- **Archivos JavaScript** - Eliminación de contenido HTML mezclado

---

## 📚 Documentación de la API

Además de la documentación automática de FastAPI, este repositorio incluye una guía técnica detallada:

### 📡 WebSockets en Tiempo Real

El backend implementa WebSockets para comunicación en tiempo real con las siguientes características:

#### Endpoints WebSocket

**WebSocket Privado (con autenticación):**
```
ws://localhost:8000/ws/asignacion/{id_asignacion}?token={jwt_token}
```

**WebSocket Público (sin autenticación):**
```
ws://localhost:8000/ws/public/asignacion/{id_asignacion}
```

#### Características Implementadas

- ✅ **Ping/Pong Keepalive**: El servidor envía pings cada 30 segundos para mantener la conexión activa
- ✅ **Autenticación JWT**: Validación de token y permisos de usuario
- ✅ **Control de Permisos**: Solo usuarios autorizados pueden conectarse a asignaciones específicas
- ✅ **Manejo de Errores**: Logging detallado para depuración
- ✅ **Reconexión Automática**: Soporte para reconexión del cliente
- ✅ **Mensajes Estructurados**: Formato JSON para todos los mensajes

#### Formato de Mensajes

**Ping del servidor:**
```json
{
  "type": "ping",
  "timestamp": 1625097600.123,
  "asignacion_id": 3
}
```

**Pong del cliente:**
```json
{
  "type": "pong",
  "timestamp": 1625097600.456,
  "ping_timestamp": 1625097600.123
}
```

**Actualización de estado:**
```json
{
  "type": "status_update",
  "id": "msg_123",
  "estado": "en_progreso",
  "estado_anterior": "pendiente"
}
```

**Confirmación (ACK):**
```json
{
  "type": "ack",
  "message_id": "msg_123",
  "status": "received",
  "asignacion_id": 3
}
```

#### Permisos de Acceso

Los usuarios pueden conectarse a una asignación si:

1. **Administradores**: Tienen acceso a todas las asignaciones
2. **Conductores**: Si están asignados como conductor del vehículo
3. **Tripulación**: Si son miembros de la tripulación asignada
4. **Otros**: No tienen acceso (HTTP 403)

#### Pruebas Locales

Para probar los WebSockets localmente:

```bash
# Ejecutar pruebas completas
python test_websocket_comprehensive.py

# Depurar conexión específica
python debug_websocket.py
```

#### Configuración para Producción (Railway.app)

El deployment está configurado con:

- **Procfile**: `uvicorn main:app --host 0.0.0.0 --port $PORT --ws websockets --ws-ping-interval 30 --ws-ping-timeout 60`
- **railway.json**: Configuración optimizada para WebSockets
- **Health Check**: `/health` para monitoreo
- **Timeouts**: Configurados para conexiones largas

#### Logs de Depuración

Los WebSockets incluyen logging detallado:

```
[ASIGNACION 3] Intento de conexión WebSocket
[ASIGNACION 3] Token válido para usuario admin (ID: 1)
[ASIGNACION 3] Conexión aceptada para usuario admin
[ASIGNACION 3] Ping enviado
[ASIGNACION 3] Pong recibido
```

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Guía funcional de la API:** [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
- **Guía técnica interna para el equipo:** [`DEVELOPER_GUIDE.md`](./DEVELOPER_GUIDE.md)
- **Manual de integración con API externa de rutas:** [`MANUAL_INTEGRACION_RUTAS.md`](./MANUAL_INTEGRACION_RUTAS.md)
- **Historial de cambios:** [`CHANGELOG.md`](./CHANGELOG.md)

### 📁 Archivos de Ejemplo (No incluidos en repo)

Para ejemplos de integración frontend/backend, consulta los archivos locales:
- `ejemplo-frontend.js` - Integración JavaScript con la API
- `ejemplo-backend.py` - Integración Python con APIs externas
- `benchmark_performance.py` - Pruebas de rendimiento
- `test_websockets.py` - Pruebas de WebSockets
- `setup_websocket_test.py` - Configuración de pruebas

---

## 🛠️ Instalación y Configuración

### Prerrequisitos

- **Python 3.13.12+**
- **PostgreSQL** con extensión PostGIS
- **Git**

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd smart-trash-backend
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos:**
   ```bash
   # Crear base de datos PostgreSQL
   createdb smart-trash-route

   # Ejecutar migraciones
   alembic upgrade head
   ```

5. **Configurar variables de entorno:**
   ```bash
   # El archivo .env ya está configurado correctamente
   # Verificar que contiene las variables necesarias
   ```

6. **Ejecutar servidor:**
   ```bash
   uvicorn main:app --reload
   ```

### Verificación

- **API Health Check:** `GET http://localhost:8000/health`
- **Documentación:** `http://localhost:8000/docs`
- **Tests:** `pytest tests/ -v`

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ --cov=.

# Tests específicos
pytest tests/test_api.py::test_root_returns_success -v
```

**Estado actual:** ✅ 8/8 tests pasan

---

## 🔒 Seguridad

- **JWT Authentication** con expiración configurable
- **RBAC (Role-Based Access Control)** con 4 roles
- **CORS configurado** para orígenes específicos
- **Validación de datos** con Pydantic
- **Hashing de contraseñas** con bcrypt

---

## 📊 Rendimiento

- **Programación asíncrona** completa con `async/await`
- **Conexiones WebSocket** optimizadas
- **Base de datos PostgreSQL** con índices optimizados
- **Cache implementado** para APIs externas
- **Rate limiting** disponible para configuración

---

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto

- **Desarrolladores:** Jose Luis Prado Valencia, Heiner Jair Godoy Zamora
- **Proyecto:** Smart Trash Routes
- **Versión:** 1.0.3
- **Fecha:** Abril 2026

---

## 📋 Formato de Respuesta Unificado

Todas las rutas devuelven el siguiente formato estándar:

- `success: true` (operaciones exitosas):

```json
{
  "success": true,
  "message": "Operación completada correctamente.",
  "data": { ... }
}
```

- `success: false` (errores):

```json
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "Recurso no encontrado.",
    "details": null,
    "path": "/ruta",
    "method": "GET",
    "timestamp": "2026-04-02T18:00:00+00:00"
  }
}
```

Esto facilita el consumo de la API desde clientes móviles y web, y reduce lógica extra en el frontend.

---

## 🏗️ Tecnologías Utilizadas

| Área                                | Herramientas                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Backend**                         | FastAPI, SQLAlchemy async, pip                                                                   |
| **Base de Datos**                   | PostgreSQL + PostGIS + `asyncpg`                                                                 |
| **Autenticación**                   | JWT, bcrypt                                                                                      |
| **WebSockets**                      | WebSockets nativo de FastAPI                                                                     |
| **Validación**                      | Pydantic                                                                                          |
| **Testing**                         | pytest, httpx                                                                                     |
| **Migraciones**                     | Alembic                                                                                           |
| **Documentación**                   | Swagger UI, ReDoc                                                                                 |