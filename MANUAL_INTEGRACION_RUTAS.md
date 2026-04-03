# 📖 Manual de Integración con API Externa de Rutas

## 🎯 Propósito

Este manual explica cómo usar la integración entre tu API de asignaciones de vehículos y una API externa de rutas. La integración permite validar automáticamente que las rutas existen antes de crear asignaciones.

## ⚙️ Configuración

He creado un archivo `configuracion-integracion.py` con ejemplos detallados de configuración:

### Variables de Entorno (.env)

```env
# URL de tu API de rutas externa
RUTAS_API_URL=http://localhost:8001

# Autenticación (si es requerida por tu API)
RUTAS_API_TOKEN=tu_token_jwt
RUTAS_API_KEY=tu_api_key

# Timeouts y reintentos
RUTAS_TIMEOUT=10.0
RUTAS_MAX_RETRIES=3
```

### Configuración por Entorno

- **Desarrollo**: `RUTAS_API_URL=http://localhost:8001`
- **Staging**: `RUTAS_API_URL=https://api-rutas-staging.tudominio.com`
- **Producción**: `RUTAS_API_URL=https://api-rutas.tudominio.com`

### Verificación de Configuración

Ejecuta para verificar que todo esté configurado:

```bash
python configuracion-integracion.py
```

## 🔄 Flujo de Trabajo

### Paso 1: Crear ruta en API externa

Desde tu frontend, crea primero la ruta en la API externa:

```javascript
// Ejemplo con fetch
const crearRuta = async (datosRuta) => {
  const response = await fetch('http://tu-api-rutas.com:8000/rutas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      origen: "Punto A",
      destino: "Punto B",
      distancia: 10.5,
      // otros campos según tu API de rutas
    })
  });

  const data = await response.json();
  return data.id_ruta; // Guardar este ID
};
```

## 📱 Ejemplo de Integración Frontend

He creado un archivo `ejemplo-frontend.js` que muestra cómo usar la integración desde JavaScript:

```javascript
// Flujo completo: Login → Crear ruta → Crear asignación
async function ejemploCompleto() {
  // 1. Login para obtener token JWT
  const loginExitoso = await login('admin@example.com', 'password123');
  
  // 2. Crear ruta en API externa
  const idRuta = await crearRutaEnAPIExterna({
    origen: 'Centro de Buenaventura',
    destino: 'Barrio Nuevo',
    distancia: 5.2,
    tiempo_estimado: 25
  });
  
  // 3. Crear asignación usando el ID de ruta
  const asignacion = await crearAsignacion(idRuta, 1, '2026-04-02T08:00:00');
}
```

### Funciones Disponibles:

- `login(email, password)` - Autenticación
- `crearRutaEnAPIExterna(datosRuta)` - Crear ruta en tu API
- `obtenerDetallesRuta(idRuta)` - Obtener detalles de ruta
- `crearAsignacion(idRuta, idVehiculo, fecha)` - Crear asignación

### Configuración:

```javascript
const API_RUTAS_URL = 'http://localhost:8001';  // Tu API de rutas
const API_ASIGNACIONES_URL = 'http://localhost:8000';  // Esta API
```

Para usar en HTML:
```html
<script src="ejemplo-frontend.js"></script>
<script>
  // Ejecutar ejemplo
  ejemploCompleto();
</script>
```

## 🐍 Ejemplo de Integración Backend

También he creado `ejemplo-backend.py` para usar la integración desde Python:

```python
import asyncio
import httpx

async def ejemplo_completo():
    # 1. Login
    await login('admin@example.com', 'password123')
    
    # 2. Crear ruta en API externa
    id_ruta = await crear_ruta_en_api_externa({
        'origen': 'Centro de Buenaventura',
        'destino': 'Barrio Nuevo',
        'distancia': 5.2,
        'tiempo_estimado': 25
    })
    
    # 3. Crear asignación
    asignacion = await crear_asignacion(id_ruta, 1, '2026-04-02T08:00:00')

asyncio.run(ejemplo_completo())
```

Ejecuta: `python ejemplo-backend.py`

## 📋 Endpoints Disponibles

### Crear Asignación (con validación automática)

```http
POST /admin/asignaciones
Authorization: Bearer <token>
Content-Type: multipart/form-data

id_ruta=123
id_vehiculo=456
fecha=2026-04-02T10:00:00
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "data": {
    "id_asignacion": 789,
    "id_ruta": "123",
    "id_vehiculo": 456,
    "estado": "pendiente",
    "fecha": "2026-04-02T10:00:00",
    "created_at": "2026-04-02T09:00:00Z"
  },
  "message": "Asignación creada exitosamente."
}
```

**Error si la ruta no existe:**
```json
{
  "success": false,
  "error": {
    "code": "bad_request",
    "message": "La ruta con id 123 no existe en el servicio de rutas.",
    "details": null,
    "path": "/admin/asignaciones",
    "method": "POST",
    "timestamp": "2026-04-02T09:00:00Z"
  }
}
```

### Consultar Detalles de Ruta

```http
GET /admin/asignaciones/rutas/{id_ruta}
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id_ruta": 123,
    "origen": "Punto A",
    "destino": "Punto B",
    "distancia": 10.5,
    "tiempo_estimado": 30
  },
  "message": "Detalles de ruta obtenidos exitosamente."
}
```

## 🧪 Probando la Integración

### 1. Sin API externa (para desarrollo)

Si la API externa no está disponible, las validaciones fallarán. Para desarrollo, puedes:

- Configurar `RUTAS_API_URL` a una URL que no exista → Todas las validaciones fallarán
- Crear un mock server simple para testing

### 2. Con API externa mock

Crea un servidor simple para testing:

```python
# mock_server.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()

rutas_db = {
    "123": {"id_ruta": 123, "origen": "A", "destino": "B"},
    "456": {"id_ruta": 456, "origen": "C", "destino": "D"}
}

@app.get("/rutas/{id_ruta}")
def obtener_ruta(id_ruta: str):
    if id_ruta in rutas_db:
        return rutas_db[id_ruta]
    return {"error": "Ruta no encontrada"}, 404

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

Ejecuta: `python mock_server.py`

### 3. Testing con Postman/Swagger

1. **Crear asignación con ruta existente:**
   - POST `/admin/asignaciones`
   - `id_ruta=123`, `id_vehiculo=1`
   - Debería funcionar ✅

2. **Crear asignación con ruta inexistente:**
   - POST `/admin/asignaciones`
   - `id_ruta=999`, `id_vehiculo=1`
   - Debería fallar con 400 ❌

3. **Consultar detalles de ruta:**
   - GET `/admin/asignaciones/rutas/123`
   - Debería devolver los detalles ✅

## 🚨 Manejo de Errores

### API externa no disponible

Si la API externa no responde:
- Las validaciones fallarán
- Se lanzará error 400: "La ruta con id X no existe en el servicio de rutas."
- Revisa logs del servidor para errores de conexión

### Timeout de conexión

- Timeout configurado en 10 segundos
- Si la API externa es lenta, aumenta el timeout en `service_rutas_externo.py`

### Formato de respuesta inesperado

- La API externa debe devolver JSON con `id_ruta` al crear rutas
- Para consultas, debe devolver el objeto de ruta o 404

## 🔧 Configuración Avanzada

### Cambiar timeout

En `services/service_rutas_externo.py`:

```python
async def obtener_ruta_por_id(self, id_ruta: int) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:  # 30 segundos
            # ... resto del código
```

### Agregar autenticación a API externa

Si tu API externa requiere auth:

```python
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.get(
        f"{self.base_url}/rutas/{id_ruta}",
        headers={"Authorization": "Bearer TU_TOKEN"}
    )
```

### Logging de errores

Los errores de conexión se imprimen en consola. Para logging más avanzado:

```python
import logging

logger = logging.getLogger(__name__)

# En lugar de print()
logger.error(f"Error conectando con API de rutas: {e}")
```

## 📝 Checklist de Implementación

- [ ] Configurar `RUTAS_API_URL` en `.env`
- [ ] Verificar que API externa esté ejecutándose
- [ ] Probar creación de asignación con ruta válida
- [ ] Probar creación de asignación con ruta inválida
- [ ] Verificar endpoint de consulta de detalles
- [ ] Configurar manejo de errores en frontend
- [ ] Documentar para otros desarrolladores

## 🎯 Próximos Pasos

1. **Implementa tu API de rutas** con los endpoints requeridos
2. **Configura la URL** en producción
3. **Agrega manejo de errores** en el frontend
4. **Considera caching** si las consultas son frecuentes
5. **Implementa reintentos** para fallos temporales

¡La integración está lista para usar! 🚀</content>
<parameter name="filePath">c:/Users/haine/OneDrive/Escritorio/smart-trash-backend/MANUAL_INTEGRACION_RUTAS.md