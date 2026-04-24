# Smart Trash Route - Diagramas de Flujo ASCII

Este documento contiene los diagramas de flujo principales del sistema Smart Trash Route.

## 1. Flujo de Inicio de Recorrido (Driver → API Externa → Admin WebSocket)

```
┌─────────────┐    POST    ┌─────────────────┐    Validar    ┌──────────────────┐    POST    ┌──────────────────┐
│   Driver    │ ──────────► │  Smart Trash   │ ─────────────► │   Validación    │ ─────────► │   API Externa   │
│  (Móvil)   │            │     API        │              │    de Reglas    │            │   de Rutas      │
└─────────────┘            └─────────────────┘              └──────────────────┘            └──────────────────┘
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          ▼                               ▼                               ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    1. Validar Tripulación                  │
       │                 │                    • ¿Tiene piloto asignado?            │
       │                 │                    • ¿Vehículo disponible?               │
       │                 │                    • ¿Asignación en estado pendiente?    │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    2. Si todo OK → Llamar API Externa        │
       │                 │                    POST /api/recorridos/iniciar              │
       │                 │                    Payload: {ruta_id, vehiculo_id, perfil_id} │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    3. Guardar respuesta                      │
       │                 │                    • recorrido_externo_id                   │
       │                 │                    • Cambiar estado a "en_curso"           │
       │                 │                    • hora_salida = timestamp actual         │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    4. Notificar WebSocket                   │
       │                 │                    ws://admin/asignacion/{id}              │
       │                 │                    Evento: "recorrido_iniciado"            │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          ▼
       ▼                 ┌─────────────────────────────────────────────────────────────────────┐
┌─────────────┐           │                    5. Respuesta al Driver                  │
│   Driver    │ ◄───────── │                    • 200 OK + datos de asignación        │
│  (Móvil)   │           └─────────────────────────────────────────────────────────────────────┘
└─────────────┘
```

## 2. Flujo de Registro de Posición (Driver → Backend → Admin WebSocket)

```
┌─────────────┐    POST    ┌─────────────────┐    Validar    ┌──────────────────┐    Guardar    ┌──────────────────┐
│   Driver    │ ──────────► │  Smart Trash   │ ─────────────► │   Validación    │ ──────────► │   Base de      │
│  (Móvil)   │            │     API        │              │    de Reglas    │             │    Datos        │
└─────────────┘            └─────────────────┘              └──────────────────┘             └──────────────────┘
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          ▼                               ▼                               ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    1. Validar Posición                     │
       │                 │                    • ¿Asignación en "en_curso"?          │
       │                 │                    • ¿Lat/Lon válidas?                   │
       │                 │                    • ¿Timestamp válido?                   │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    2. Almacenar en BD                     │
       │                 │                    Tabla: RecorridoPosicion              │
       │                 │                    • lat, lon, accuracy, speed, bearing     │
       │                 │                    • timestamp del dispositivo              │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    3. Emitir WebSocket                   │
       │                 │                    ws://admin/asignacion/{id}              │
       │                 │                    Evento: "posicion_actualizada"         │
       │                 │                    • lat, lon, speed, timestamp          │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    4. Tarea Periódica (5s)             │
       │                 │                    • Broadcast automático a todos los       │
       │                 │                      clientes conectados                   │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          ▼
       ▼                 ┌─────────────────────────────────────────────────────────────────────┐
┌─────────────┐           │                    5. Respuesta al Driver                  │
│   Driver    │ ◄───────── │                    • 201 Created + ID de posición        │
│  (Móvil)   │           └─────────────────────────────────────────────────────────────────────┘
└─────────────┘
```

## 3. Flujo de Finalización de Recorrido (Driver → API Externa → Backend)

```
┌─────────────┐    POST    ┌─────────────────┐    Validar    ┌──────────────────┐    POST    ┌──────────────────┐
│   Driver    │ ──────────► │  Smart Trash   │ ─────────────► │   Validación    │ ─────────► │   API Externa   │
│  (Móvil)   │            │     API        │              │    de Reglas    │            │   de Rutas      │
└─────────────┘            └─────────────────┘              └──────────────────┘            └──────────────────┘
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          ▼                               ▼                               ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    1. Validar Finalización                 │
       │                 │                    • ¿Asignación en "en_curso"?          │
       │                 │                    • ¿No excede 24 horas?                │
       │                 │                    • ¿Existe recorrido_externo_id?      │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    2. Llamar API Externa                │
       │                 │                    POST /api/recorridos/{id}/finalizar     │
       │                 │                    Payload: {perfil_id}                   │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    3. Manejar Respuesta                  │
       │                 │                    • Si éxito → Actualizar estado externo   │
       │                 │                    • Si error → Registrar IntentoPosicion │
       │                 │                    • Siempre → Cambiar a "completada"   │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    4. Actualizar Estado Local              │
       │                 │                    • estado = "completada"               │
       │                 │                    • vehiculo.estado = "disponible"       │
       │                 │                    • hora_llegada = timestamp actual     │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    5. Notificar WebSocket                   │
       │                 │                    ws://admin/asignacion/{id}              │
       │                 │                    Evento: "recorrido_finalizado"         │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       ▼                 ┌─────────────────────────────────────────────────────────────────────┐
┌─────────────┐           │                    6. Respuesta al Driver                  │
│   Driver    │ ◄───────── │                    • 200 OK + datos de asignación        │
│  (Móvil)   │           └─────────────────────────────────────────────────────────────────────┘
└─────────────┘
```

## 4. Flujo de Subida de Fotos (Driver → Backend → Admin)

```
┌─────────────┐    POST    ┌─────────────────┐    Validar    ┌──────────────────┐    Procesar   ┌──────────────────┐
│   Driver    │ ──────────► │  Smart Trash   │ ─────────────► │   Validación    │ ──────────► │   Base64       │
│  (Móvil)   │            │     API        │              │    de Imagen    │             │   Decoder      │
└─────────────┘            └─────────────────┘              └──────────────────┘             └──────────────────┘
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          ▼                               ▼                               ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    1. Validar Foto                        │
       │                 │                    • ¿Formato data:image/*;base64 válido? │
       │                 │                    • ¿Tamaño < 10MB?                    │
       │                 │                    • ¿Tipo válido? (recoleccion/incidencia/cumplimiento) │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    2. Decodificar Base64                  │
       │                 │                    • Extraer MIME type                    │
       │                 │                    • Decodificar a bytes                   │
       │                 │                    • Validar headers de imagen            │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    3. Almacenar Imagen                   │
       │                 │                    • Generar nombre único                   │
       │                 │                    • Guardar en storage                   │
       │                 │                    • Generar URL de acceso                │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    4. Guardar en BD                        │
       │                 │                    Tabla: RecorridoFoto                  │
       │                 │                    • url, tipo, timestamp_captura        │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    5. Notificar WebSocket                   │
       │                 │                    ws://admin/asignacion/{id}              │
       │                 │                    Evento: "foto_registrada"             │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       ▼                 ┌─────────────────────────────────────────────────────────────────────┐
┌─────────────┐           │                    6. Respuesta al Driver                  │
│   Driver    │ ◄───────── │                    • 201 Created + URL de foto          │
│  (Móvil)   │           └─────────────────────────────────────────────────────────────────────┘
└─────────────┘
```

## 5. Flujo de Conexión WebSocket (Admin → Real-time)

```
┌─────────────┐    WebSocket    ┌─────────────────┐    Validar    ┌──────────────────┐    Conectar    ┌──────────────────┐
│   Admin     │ ──────────────► │  Smart Trash   │ ─────────────► │   JWT Token     │ ───────────► │  WebSocket     │
│ Dashboard   │                │     API        │              │    Verifier     │              │   Manager     │
└─────────────┘                └─────────────────┘              └──────────────────┘              └──────────────────┘
       │                             │                               │                               │
       │                             │                               │                               │
       │                             │                               │                               │
       │                             │                               │                               │
       │                             ▼                               ▼                               ▼
       │                    ┌─────────────────────────────────────────────────────────────────────┐
       │                    │                    1. Validar Conexión                    │
       │                    │                    • ¿Token JWT válido?                   │
       │                    │                    • ¿Usuario rol = "admin"?            │
       │                    │                    • ¿Asignación existe?                │
       │                    └─────────────────────────────────────────────────────────────────────┘
       │                             │
       │                             │
       │                             │
       │                             ▼
       │                    ┌─────────────────────────────────────────────────────────────────────┐
       │                    │                    2. Aceptar Conexión                    │
       │                    │                    • Agregar a grupo de asignación        │
       │                    │                    • Iniciar tarea periódica (5s)        │
       │                    └─────────────────────────────────────────────────────────────────────┘
       │                             │
       │                             │
       │                             │
       │                             ▼
       │                    ┌─────────────────────────────────────────────────────────────────────┐
       │                    │                    3. Eventos Recibidos (cada 5s)       │
       │                    │                    • posicion_actualizada                  │
       │                    │                    • estado_cambio                       │
       │                    │                    • tripulacion_evento                  │
       │                    └─────────────────────────────────────────────────────────────────────┘
       │                             │
       │                             │
       │                             │
       │                             ▼
       │                    ┌─────────────────────────────────────────────────────────────────────┐
       │                    │                    4. Manejo de Desconexión              │
       │                    │                    • Remover del grupo                   │
       │                    │                    • Cancelar tarea periódica             │
       │                    │                    • Limpiar recursos                    │
       │                    └─────────────────────────────────────────────────────────────────────┘
       │                             │
       │                             │
       │                             │
       │                             ▼
       ▼                    ┌─────────────────────────────────────────────────────────────────────┐
┌─────────────┐          │                    5. UI Dashboard Actualizada              │
│   Admin     │ ◄────────── │                    • Mapa en tiempo real                 │
│ Dashboard   │          │                    • Estado del recorrido               │
│             │          │                    • Lista de eventos                   │
└─────────────┘          └─────────────────────────────────────────────────────────────────────┘
```

## 6. Flujo de Validación de Tripulación con Piloto

```
┌─────────────┐    POST    ┌─────────────────┐    Consultar    ┌──────────────────┐    Validar    ┌──────────────────┐
│   Admin     │ ──────────► │  Smart Trash   │ ─────────────► │   Tripulación   │ ─────────────► │   Reglas de    │
│ Dashboard   │            │     API        │              │    Asignada    │              │   Negocio      │
└─────────────┘            └─────────────────┘              └──────────────────┘              └──────────────────┘
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          ▼                               ▼                               ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    1. Obtener Asignación                  │
       │                 │                    • Cargar con relaciones              │
       │                 │                    • tripulacion.miembros.usuario        │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    2. Verificar Tripulación                │
       │                 │                    • ¿Existe tripulación asignada?       │
       │                 │                    • ¿Hay miembros en la tripulación?    │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    3. Buscar Piloto                      │
       │                 │                    • Iterar miembros de tripulación      │
       │                 │                    • ¿Alguien con rol_tripulacion = "piloto"? │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    4. Retornar Resultado                  │
       │                 │                    • Si hay piloto → 200 OK              │
       │                 │                    • Si no hay piloto → 400 Bad Request  │
       │                 │                    • Mensaje: "La tripulación debe tener al menos 1 conductor" │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       ▼                 ┌─────────────────────────────────────────────────────────────────────┐
┌─────────────┐           │                    5. Respuesta al Admin                   │
│   Admin     │ ◄───────── │                    • {valid: true, message: "..."}      │
│ Dashboard   │           │                    • O {detail: "La tripulación debe..."} │
└─────────────┘           └─────────────────────────────────────────────────────────────────────┘
```

## 7. Flujo de Manejo de Errores API Externa

```
┌─────────────────┐    POST    ┌─────────────────┐    Error     ┌──────────────────┐    Registrar    ┌──────────────────┐
│ Smart Trash   │ ──────────► │   API Externa   │ ───────────► │   Smart Trash   │ ─────────────► │   Intentos      │
│     API       │            │   de Rutas      │              │     API        │              │   Fallidos      │
└─────────────────┘            └─────────────────┘              └──────────────────┘              └──────────────────┘
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          ▼                               ▼                               ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    1. Error de API Externa                │
       │                 │                    • 500 Internal Server Error           │
       │                 │                    • Timeout                             │
       │                 │                    • Servicio no disponible               │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    2. Registrar Intento                  │
       │                 │                    Tabla: IntentoPosicion               │
       │                 │                    • payload JSON completo              │
       │                 │                    • estado = "fallido"                │
       │                 │                    • error_msg detallado                │
       │                 │                    • retry_count++                      │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    3. Continuar Operación Local            │
       │                 │                    • No bloquear flujo del driver        │
       │                 │                    • Completar recorrido localmente      │
       │                 │                    • Registrar log del error            │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    4. Notificar Diferencia                │
       │                 │                    • WebSocket: "externa_desincronizada" │
       │                 │                    • Email al administrador              │
       │                 │                    • Dashboard: alerta naranja         │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       ▼                 ┌─────────────────────────────────────────────────────────────────────┐
┌─────────────┐           │                    5. Respuesta al Cliente                │
│   Driver    │ ◄───────── │                    • 200 OK (operación completada)     │
│  (Móvil)   │           │                    • Warning en headers sobre API externa│
└─────────────┘           └─────────────────────────────────────────────────────────────────────┘
```

## 8. Flujo de Autenticación y Autorización

```
┌─────────────┐    POST    ┌─────────────────┐    Validar    ┌──────────────────┐    Generar    ┌──────────────────┐
│   Usuario   │ ──────────► │  Smart Trash   │ ─────────────► │   Credenciales │ ───────────► │   JWT Token     │
│  (Cualquiera)│            │     API        │              │    (email/pass) │              │   (Bearer)      │
└─────────────┘            └─────────────────┘              └──────────────────┘              └──────────────────┘
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          │                               │                               │
       │                          ▼                               ▼                               ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    1. Validar Credenciales               │
       │                 │                    • ¿Email existe en BD?               │
       │                 │                    • ¿Password coincide (bcrypt)?         │
       │                 │                    • ¿Usuario está activo?             │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    2. Cargar Perfil                      │
       │                 │                    • Rol del usuario (admin/driver/user)  │
       │                 │                    • Permisos asociados                 │
       │                 │                    • Información de perfil              │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    3. Generar JWT                        │
       │                 │                    • Payload: {user_id, rol, exp}       │
       │                 │                    • Firma: HS256 con secret key         │
       │                 │                    • Validez: 1 hora                   │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       │                 ┌─────────────────────────────────────────────────────────────────────┐
       │                 │                    4. Retornar Token                      │
       │                 │                    • access_token                        │
       │                 │                    • token_type = "bearer"               │
       │                 │                    • expires_in = 3600                  │
       │                 └─────────────────────────────────────────────────────────────────────┘
       │                          │
       │                          │
       │                          │
       │                          ▼
       ▼                 ┌─────────────────────────────────────────────────────────────────────┐
┌─────────────┐           │                    5. Uso del Token                      │
│   Cliente   │ ◄───────── │                    • Header: Authorization: Bearer <token> │
│   (Móvil/Web)│          │                    • Query param: ?token=<token> (WS)   │
└─────────────┘           │                    • Middleware verifica cada request      │
                       └─────────────────────────────────────────────────────────────────────┘
```

---

## Leyenda de Símbolos

```
┌─────────────┐ = Actor/Entidad (Driver, Admin, API, etc.)
│   Texto    │
└─────────────┘

─────► = Flujo principal de datos/peticiones
◄──── = Respuesta/retorno de datos
│     = Conexión o flujo vertical
▼     = Punto de decisión o procesamiento
```

## Notas Importantes

1. **Validación de Piloto**: Es obligatorio que toda tripulación tenga al menos un conductor (rol_tripulacion = "piloto")
2. **API Externa**: Si falla, el sistema continúa operando localmente y registra el intento fallido
3. **WebSocket**: Los eventos se envían cada 5 segundos automáticamente a todos los clientes conectados
4. **Base64**: Las fotos se decodifican y validan antes de almacenar
5. **JWT**: Token válido por 1 hora, requerido en todos los endpoints protegidos
6. **Estados**: pendiente → en_curso → completada/cancelada
7. **24 Horas**: Límite máximo para finalizar un recorrido desde su inicio
