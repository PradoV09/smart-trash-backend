# Smart Trash Route API - Ejemplos cURL

Este documento contiene ejemplos completos para probar todos los endpoints de la API Smart Trash Route.

## Configuración Base

```bash
# Variables de configuración
API_BASE="http://localhost:8000"
JWT_TOKEN="tu_jwt_token_aqui"  # Reemplazar con token válido

# Headers comunes
AUTH_HEADER="Authorization: Bearer $JWT_TOKEN"
CONTENT_TYPE="Content-Type: application/json"
```

## 1. Autenticación

### Login (Obtener JWT)
```bash
curl -X POST "$API_BASE/auth/login" \
  -H "$CONTENT_TYPE" \
  -d '{
    "email": "admin@smarttrash.com",
    "password": "admin123"
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "message": "Login exitoso"
}
```

## 2. Gestión de Asignaciones (Admin)

### Crear Asignación
```bash
curl -X POST "$API_BASE/admin/asignaciones" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "id_vehiculo": 1,
    "id_ruta": "RUTA-001",
    "id_tripulacion": 1,
    "fecha": "2026-04-23T08:00:00Z"
  }'
```

### Listar Asignaciones
```bash
curl -X GET "$API_BASE/admin/asignaciones" \
  -H "$AUTH_HEADER"
```

### Validar Tripulación con Piloto
```bash
curl -X POST "$API_BASE/admin/asignaciones/1/validar-piloto" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE"
```

### Obtener Detalles de Asignación
```bash
curl -X GET "$API_BASE/admin/asignaciones/1" \
  -H "$AUTH_HEADER"
```

## 3. Gestión de Asignaciones (Driver)

### Ver Asignación del Driver
```bash
curl -X GET "$API_BASE/driver/asignaciones/1" \
  -H "$AUTH_HEADER"
```

### Iniciar Recorrido (con API Externa)
```bash
curl -X POST "$API_BASE/driver/asignaciones/1/iniciar" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "perfil_id": "PERFIL-001"
  }'
```

### Finalizar Recorrido (con API Externa)
```bash
curl -X POST "$API_BASE/driver/asignaciones/1/finalizar" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "perfil_id": "PERFIL-001"
  }'
```

## 4. Posiciones GPS (Driver)

### Registrar Posición
```bash
curl -X POST "$API_BASE/driver/asignaciones/1/posiciones" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "latitud": 3.8801,
    "longitud": -77.0188,
    "accuracy": 5.2,
    "speed": 25.3,
    "bearing": 45.5,
    "timestamp": "2026-04-23T10:30:00Z"
  }'
```

### Respuesta esperada:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "id_asignacion": 1,
    "latitud": 3.8801,
    "longitud": -77.0188,
    "accuracy": 5.2,
    "speed": 25.3,
    "bearing": 45.5,
    "timestamp": "2026-04-23T10:30:00Z",
    "created_at": "2026-04-23T10:30:01Z"
  },
  "message": "Posición registrada exitosamente."
}
```

## 5. Posiciones GPS (Admin)

### Listar Posiciones con Paginación
```bash
curl -X GET "$API_BASE/admin/asignaciones/1/posiciones?page=1&page_size=50" \
  -H "$AUTH_HEADER"
```

### Obtener Última Posición
```bash
curl -X GET "$API_BASE/admin/asignaciones/1/posiciones/ultima" \
  -H "$AUTH_HEADER"
```

## 6. Fotos/Evidencia (Driver)

### Subir Foto en Base64
```bash
curl -X POST "$API_BASE/driver/asignaciones/1/fotos" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A8A",
    "timestamp": "2026-04-23T10:30:00Z",
    "tipo": "recoleccion"
  }'
```

### Respuesta esperada:
```json
{
  "success": true,
  "data": {
    "id": 456,
    "id_asignacion": 1,
    "url": "https://storage.smarttrash.com/fotos/asignacion_1_456.jpg",
    "tipo": "recoleccion",
    "timestamp_captura": "2026-04-23T10:30:00Z",
    "timestamp_envio": "2026-04-23T10:30:05Z"
  },
  "message": "Foto registrada exitosamente."
}
```

## 7. Fotos/Evidencia (Admin)

### Listar Fotos de Asignación
```bash
curl -X GET "$API_BASE/admin/asignaciones/1/fotos" \
  -H "$AUTH_HEADER"
```

## 8. Estado en Vivo (Admin)

### Obtener Estado Vivo
```bash
curl -X GET "$API_BASE/admin/asignaciones/1/estado-vivo" \
  -H "$AUTH_HEADER"
```

### Respuesta esperada:
```json
{
  "success": true,
  "data": {
    "id_asignacion": 1,
    "estado": "en_curso",
    "ubicacion_actual": {
      "latitud": 3.8801,
      "longitud": -77.0188,
      "timestamp": "2026-04-23T10:30:00Z",
      "accuracy": 5.2,
      "speed": 25.3,
      "bearing": 45.5
    },
    "ultimo_hito": "Punto de recolección #3",
    "miembros_tripulacion": [
      {
        "id_usuario": 1,
        "nombre": "Juan Pérez",
        "rol_tripulacion": "piloto",
        "confirmado": true
      },
      {
        "id_usuario": 2,
        "nombre": "Carlos López",
        "rol_tripulacion": "recolector",
        "confirmado": true
      }
    ],
    "hora_salida": "2026-04-23T08:00:00Z",
    "tiempo_transcurrido": 9000,
    "distancia_recorrida": 15.2,
    "ultima_actualizacion": "2026-04-23T10:30:00Z"
  },
  "message": "Estado vivo obtenido exitosamente."
}
```

## 9. WebSocket (Admin) - Prueba con wscat

### Conexión WebSocket para Seguimiento en Vivo
```bash
# Instalar wscat: npm install -g wscat
wscat -c "ws://localhost:8000/ws/admin/asignacion/1?token=$JWT_TOKEN"
```

### Eventos recibidos (cada 5 segundos):

#### Posición Actualizada
```json
{
  "evento": "posicion_actualizada",
  "id_asignacion": 1,
  "timestamp": "2026-04-23T10:30:00Z",
  "data": {
    "lat": 3.8801,
    "lon": -77.0188,
    "velocidad": 25.3,
    "ultimo_hito": "Punto de recolección #4"
  }
}
```

#### Cambio de Estado
```json
{
  "evento": "estado_cambio",
  "id_asignacion": 1,
  "timestamp": "2026-04-23T08:00:00Z",
  "data": {
    "estado_anterior": "pendiente",
    "estado_nuevo": "en_curso"
  }
}
```

#### Evento de Tripulación
```json
{
  "evento": "tripulacion_evento",
  "id_asignacion": 1,
  "timestamp": "2026-04-23T08:05:00Z",
  "data": {
    "tipo": "confirmacion",
    "usuario": {
      "id_usuario": 2,
      "nombre": "Carlos López",
      "rol_tripulacion": "recolector"
    }
  }
}
```

## 10. Gestión de Usuarios (Admin)

### Listar Usuarios
```bash
curl -X GET "$API_BASE/admin/usuarios" \
  -H "$AUTH_HEADER"
```

### Crear Usuario Driver
```bash
curl -X POST "$API_BASE/admin/usuarios" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "email": "driver1@smarttrash.com",
    "password": "driver123",
    "nombre": "Pedro Martínez",
    "id_rol": 2
  }'
```

## 11. Gestión de Vehículos (Admin)

### Listar Vehículos
```bash
curl -X GET "$API_BASE/admin/vehiculos" \
  -H "$AUTH_HEADER"
```

### Crear Vehículo
```bash
curl -X POST "$API_BASE/admin/vehiculos" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "placa": "ABC-123",
    "marca": "Mercedes-Benz",
    "modelo": "Actros",
    "capacidad": 8000,
    "anio": 2022
  }'
```

## 12. Health Check

### Verificar Estado de la API
```bash
curl -X GET "$API_BASE/health"
```

### Respuesta esperada:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2026-04-23T10:30:00Z",
    "version": "1.0.0"
  },
  "message": "API funcionando correctamente"
}
```

## 13. Escenarios de Error

### Error: Tripulación sin Piloto
```bash
curl -X POST "$API_BASE/driver/asignaciones/1/iniciar" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE"
```

**Respuesta esperada (400):**
```json
{
  "detail": "La tripulación debe tener al menos 1 conductor."
}
```

### Error: Vehículo ya en Ruta
```bash
curl -X POST "$API_BASE/driver/asignaciones/1/iniciar" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE"
```

**Respuesta esperada (400):**
```json
{
  "detail": "El vehículo 1 ya tiene un recorrido activo."
}
```

### Error: Recorrido excede 24 horas
```bash
curl -X POST "$API_BASE/driver/asignaciones/1/finalizar" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE"
```

**Respuesta esperada (400):**
```json
{
  "detail": "No se puede finalizar el recorrido: ha excedido las 24 horas permitidas."
}
```

### Error: Token Inválido
```bash
curl -X GET "$API_BASE/admin/asignaciones" \
  -H "Authorization: Bearer token_invalido"
```

**Respuesta esperada (401):**
```json
{
  "detail": "Could not validate credentials"
}
```

## 14. Tips para Testing

### 1. Usar Variables de Entorno
```bash
export API_BASE="http://localhost:8000"
export JWT_TOKEN="tu_token_aqui"
```

### 2. Formatear JSON
```bash
curl ... | jq '.'
```

### 3. Guardar Respuestas
```bash
curl -X GET "$API_BASE/admin/asignaciones" \
  -H "$AUTH_HEADER" \
  -o response.json
```

### 4. Testing de Carga
```bash
# 10 peticiones simultáneas
for i in {1..10}; do
  curl -X POST "$API_BASE/driver/asignaciones/1/posiciones" \
    -H "$AUTH_HEADER" \
    -H "$CONTENT_TYPE" \
    -d "{
      \"latitud\": 3.880$i,
      \"longitud\": -77.018$i,
      \"timestamp\": \"2026-04-23T10:30:$i\"Z
    }" &
done
wait
```

### 5. WebSocket con Script
```javascript
// test-websocket.js
const WebSocket = require('ws');
const token = 'tu_jwt_token_aqui';
const ws = new WebSocket(`ws://localhost:8000/ws/admin/asignacion/1?token=${token}`);

ws.on('open', function open() {
  console.log('Conectado al WebSocket');
});

ws.on('message', function message(data) {
  console.log('Evento recibido:', JSON.parse(data));
});

ws.on('close', function close() {
  console.log('Desconectado del WebSocket');
});
```

Ejecutar: `node test-websocket.js`

---

**Nota:** Reemplaza los valores de ejemplo (IDs, tokens, etc.) con datos válidos de tu base de datos antes de ejecutar las pruebas.

Todo lo que tiene que ver con la rutas publicas se puede acceder sin token


/publico/rutas/activas 

/publico/rutas/horario   

