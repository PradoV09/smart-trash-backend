# Información del API para Conectar Mapas a Rutas - Driver

## Pregunta 1: ¿En qué campo viene la ruta en GET /driver/asignaciones?

**Respuesta:** La ruta viene como un **objeto dict completo** en el campo `ruta` de la asignación.

### Estructura de respuesta:

```json
{
  "id_asignacion": 1,
  "id_vehiculo": 5,
  "id_ruta": "550e8400-e29b-41d4-a716-446655440000",
  "fecha": "2024-05-13T10:00:00Z",
  "hora_salida": null,
  "estado": "pendiente",
  "created_at": "2024-05-13T09:30:00Z",
  "vehiculo": { ... },
  "tripulacion": { ... },
  "ruta": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre_ruta": "Ruta Principal Centro",
    "perfil_id": "...",
    "color_hex": "#FF0000",
    "shape": [
      { "lat": -12.0456, "lon": -77.0422 },
      { "lat": -12.0467, "lon": -77.0433 },
      { "lat": -12.0478, "lon": -77.0444 }
    ],
    "created_at": "2024-01-15T08:00:00Z",
    "updated_at": "2024-05-10T15:30:00Z"
  }
}
```

### Puntos clave:

- **Campo `ruta`:** Viene como un objeto dict (NO es null)
- **Campo `ruta.shape`:** Array de puntos con latitud y longitud
- **Campo `ruta.id`:** El ID único de la ruta (UUID)
- **Campo `ruta.nombre_ruta`:** Nombre descriptivo
- **Campo `ruta.color_hex`:** Color de la ruta para visualización

---

## Pregunta 2: ¿Hay un endpoint para obtener los puntos de la ruta?

**Respuesta:** Sí, existen dos opciones:

### Opción 1: Desde la asignación del driver (RECOMENDADO)

```http
GET /driver/asignaciones/{id_asignacion}
```

**Ventaja:** Ya viene enriquecida con todos los datos de la ruta, incluyendo `shape` con los puntos.

### Opción 2: Endpoint de admin (si necesitas actualizar puntos)

```http
GET /admin/asignaciones/rutas/{id_ruta}
```

**Retorna:** El objeto ruta completo con shape:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre_ruta": "Ruta Principal Centro",
  "shape": [
    { "lat": -12.0456, "lon": -77.0422 },
    { "lat": -12.0467, "lon": -77.0433 }
  ],
  "perfil_id": "...",
  "color_hex": "#FF0000",
  "created_at": "...",
  "updated_at": "..."
}
```

---

## Implementación en Frontend

### En React/Vue, cuando el driver carga su asignación:

```javascript
// 1. Obtener la asignación del driver
const response = await fetch('/driver/asignaciones/{id_asignacion}');
const { data: asignacion } = await response.json();

// 2. Acceder directamente a los puntos de la ruta
const rutaPoints = asignacion.ruta.shape;

// 3. Renderizar en el mapa
rutaPoints.forEach((point) => {
  marcar_punto_en_mapa(point.lat, point.lon);
});

// 4. Obtener info adicional
const nombreRuta = asignacion.ruta.nombre_ruta;
const colorRuta = asignacion.ruta.color_hex;
```

---

## Notas técnicas

- La ruta se enriquece automáticamente en el backend llamando a la API externa de rutas
- El backend almacena solo el `id_ruta` en la BD, pero enriquece la respuesta con `shape` al consultar
- Si la API de rutas falla, el campo `ruta` será `null` pero la asignación se retorna correctamente
- Los puntos en `shape` están en orden secuencial del recorrido

---

## Archivos de referencia en el código

- Router: `routers/router_asignacionrutas.py`
- Controller: `controllers/controller_asignacionrutas.py`
- Service: `services/service_asignacionrutas.py` (método `_enriquecer_con_rutas`)
- Schema: `schemas/schema_asignacionrutas.py` (AsignacionResponse con campo ruta)
