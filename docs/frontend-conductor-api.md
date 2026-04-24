# API Frontend Conductor - Documentación

## Base URL
```
http://localhost:8000
```

## Autenticación
Todos los endpoints requieren token JWT en header:
```
Authorization: Bearer <token_jwt>
```

---

## 1. Iniciar Sesión
```http
POST /auth/login
Content-Type: application/json

{
  "username": "ciyeey",
  "password": "contraseña"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 28800
}
```

---

## 2. Ver Asignaciones Pendientes
```http
GET /driver/asignaciones
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_asignacion": 3,
      "id_ruta": "019db226-aec1-70f8-9db2-ee0a8e3806d3",
      "fecha": "2026-04-23T19:25:00Z",
      "estado": "pendiente",
      "vehiculo": {
        "id_vehiculo": 1,
        "placa": "ABC123",
        "modelo": "BMA",
        "capacidad_m3": 123.987
      },
      "tripulacion": {
        "id_tripulacion": 4,
        "nombre": "78uu",
        "miembros": [
          {
            "id": 1,
            "rol_tripulacion": "conductor",
            "usuario": {
              "username": "ciyeey",
              "correo": "chirstian@gmail.com"
            }
          }
        ]
      }
    }
  ]
}
```

---

## 3. Iniciar Recorrido
```http
POST /driver/asignaciones/{id_asignacion}/iniciar
Authorization: Bearer <token>
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Recorrido iniciado exitosamente.",
  "data": {
    "id_asignacion": 3,
    "estado": "en_curso",
    "hora_salida": "2026-04-24T19:57:09.714194Z",
    "vehiculo": {
      "estado": "en_ruta"
    }
  }
}
```

---

## 4. Finalizar Recorrido
```http
POST /driver/asignaciones/{id_asignacion}/finalizar
Authorization: Bearer <token>
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Recorrido finalizado exitosamente.",
  "data": {
    "id_asignacion": 3,
    "estado": "completada",
    "vehiculo": {
      "estado": "disponible"
    }
  }
}
```

---

## 5. WebSocket - Eventos en Tiempo Real

Conectar a:
```
ws://localhost:8000/ws
```

**Eventos recibidos:**

### Recorrido Iniciado
```json
{
  "evento": "recorrido_iniciado",
  "id_asignacion": 3,
  "recorrido_externo_id": "uuid-del-recorrido",
  "hora_salida": "2026-04-24T19:57:09.714194Z",
  "estado": "en_curso"
}
```

### Recorrido Finalizado
```json
{
  "evento": "recorrido_finalizado",
  "id_asignacion": 3,
  "estado": "completada"
}
```

---

## Flujo Completo del Conductor

### 1. Login
- Obtener token JWT
- Guardar en localStorage

### 2. Ver Asignaciones
- GET `/driver/asignaciones`
- Filtrar las que están en estado `pendiente`

### 3. Iniciar Recorrido
- POST `/driver/asignaciones/{id}/iniciar`
- Actualizar UI a estado `en_curso`
- Escuchar eventos WebSocket

### 4. Finalizar Recorrido
- POST `/driver/asignaciones/{id}/finalizar`
- Actualizar UI a estado `completada`

---

## Estados de Asignación

| Estado | Descripción | Acciones Permitidas |
|--------|-------------|-------------------|
| `pendiente` | Esperando inicio | ✅ Iniciar |
| `en_curso` | Recorrido activo | ✅ Finalizar |
| `completada` | Recorrido finalizado | ❌ Ninguna |
| `cancelada` | Asignación cancelada | ❌ Ninguna |

---

## Estados del Vehículo

| Estado | Descripción |
|--------|-------------|
| `disponible` | Libre para nueva asignación |
| `en_ruta` | En recorrido activo |
| `mantenimiento` | En mantenimiento |

---

## Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| 401 | No autorizado | Renovar token |
| 404 | Asignación no encontrada | Verificar ID |
| 400 | Estado no válido | Verificar flujo |
| 502 | Error API externa | Reintentar más tarde |

---

## Ejemplo de Implementación (React)

```javascript
// Login
const login = async (username, password) => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
};

// Iniciar recorrido
const iniciarRecorrido = async (idAsignacion) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`/driver/asignaciones/${idAsignacion}/iniciar`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return await response.json();
};
```

---

## Notas Importantes

1. **Token Expiración**: 8 horas (28800 segundos)
2. **WebSocket**: Opcional pero recomendado para UI en tiempo real
3. **Manejo de Errores**: Siempre verificar `success: false` en respuestas
4. **Timezone**: Todas las fechas en UTC
