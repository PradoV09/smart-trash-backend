"""
CAMBIOS NECESARIOS EN SERVICIOS EXISTENTES

Este archivo documenta y proporciona el código para modificar los servicios
existentes para usar ExternalSyncService centralizado.

ARCHIVOS A MODIFICAR:

1. services/service_vehiculo.py
2. services/service_posiciones.py
3. services/service_asignacionrutas.py (opcional)
   """

# ============================================================================

# 1. MODIFICACIONES EN: services/service_vehiculo.py

# ============================================================================

"""
CAMBIOS:

- Importar ExternalSyncService
- Modificar actualizar_vehiculo_por_id() para sincronizar
- Modificar cambiar_estado_vehiculo() para sincronizar
- Modificar eliminar_vehiculo() para sincronizar

NOTA: El método añadir_vehiculo() ya realiza sincronización pero será
mejorado para usar el nuevo servicio centralizado.
"""

# --- CÓDIGO ORIGINAL A REEMPLAZAR ---

# Original: actualizar_vehiculo_por_id()

async def actualizar_vehiculo_por_id(self, id_vehiculo: int, data: VehiculoUpdate) -> VehiculoResponse:
"""Actualiza parcialmente los datos de un vehículo existente."""
vehiculo = await self.\_obtener_vehiculo_orm(id_vehiculo)
for campo, valor in data.model_dump(exclude_none=True).items():
setattr(vehiculo, campo, valor)
await self.db.flush()
return await self.obtener_vehiculo_por_id(id_vehiculo)

# --- CÓDIGO NUEVO A USAR ---

async def actualizar_vehiculo_por_id(self, id_vehiculo: int, data: VehiculoUpdate) -> VehiculoResponse:
"""
Actualiza parcialmente los datos de un vehículo existente.

    Cambios:
    - Actualiza BD local primero
    - Luego sincroniza con API externa
    - Si API falla, mantiene datos locales
    """
    from services.external_sync_service import get_external_sync_service

    vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)

    # 1. Actualizar en BD local primero
    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(vehiculo, campo, valor)
    await self.db.flush()

    # 2. Sincronizar con API externa (si está configurada)
    if vehiculo.id_externo:
        sync_service = get_external_sync_service()
        if sync_service.es_sincronizacion_habilitada():
            try:
                metadata = await sync_service.sync_update_vehiculo(
                    id_externo=vehiculo.id_externo,
                    placa=vehiculo.placa if "placa" in data.model_dump(exclude_none=True) else None,
                    modelo=vehiculo.modelo if "modelo" in data.model_dump(exclude_none=True) else None,
                    capacidad_m3=vehiculo.capacidad_m3 if "capacidad_m3" in data.model_dump(exclude_none=True) else None,
                    recurso_id_local=id_vehiculo,
                )

                # Loguear resultado de sincronización
                if metadata.estado != SyncStatus.SUCCESS:
                    logger.warning(
                        f"Vehículo {id_vehiculo} actualizado localmente pero "
                        f"sincronización falló: {metadata.error_message}"
                    )
            except Exception as e:
                logger.error(f"Error sincronizando actualización de vehículo {id_vehiculo}: {e}")
                # No lanzar excepción - los datos locales se guardaron

    return await self.obtener_vehiculo_por_id(id_vehiculo)

# --- CÓDIGO ORIGINAL A REEMPLAZAR (cambiar_estado_vehiculo) ---

async def cambiar_estado_vehiculo(self, id_vehiculo: int, estado: EstadoVehiculo) -> VehiculoResponse:
"""Actualiza únicamente el estado operativo del vehículo."""
vehiculo = await self.\_obtener_vehiculo_orm(id_vehiculo)
vehiculo.estado = estado
await self.db.flush()
return await self.obtener_vehiculo_por_id(id_vehiculo)

# --- CÓDIGO NUEVO A USAR ---

async def cambiar_estado_vehiculo(self, id_vehiculo: int, estado: EstadoVehiculo) -> VehiculoResponse:
"""
Actualiza únicamente el estado operativo del vehículo.

    Cambios:
    - Actualiza BD local primero
    - Luego sincroniza el cambio de estado con API externa
    """
    from services.external_sync_service import get_external_sync_service, SyncStatus

    vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
    vehiculo.estado = estado
    await self.db.flush()

    # Sincronizar cambio de estado con API externa
    if vehiculo.id_externo:
        sync_service = get_external_sync_service()
        if sync_service.es_sincronizacion_habilitada():
            try:
                metadata = await sync_service.sync_update_vehiculo(
                    id_externo=vehiculo.id_externo,
                    estado=estado.value,
                    recurso_id_local=id_vehiculo,
                )

                if metadata.estado != SyncStatus.SUCCESS:
                    logger.warning(
                        f"Vehículo {id_vehiculo} cambió estado localmente pero "
                        f"sincronización falló: {metadata.error_message}"
                    )
            except Exception as e:
                logger.error(f"Error sincronizando cambio de estado de vehículo {id_vehiculo}: {e}")

    return await self.obtener_vehiculo_por_id(id_vehiculo)

# --- CÓDIGO ORIGINAL A REEMPLAZAR (eliminar_vehiculo) ---

async def eliminar_vehiculo(self, id_vehiculo: int) -> None:
vehiculo = await self.\_obtener_vehiculo_orm(id_vehiculo)
await self.db.delete(vehiculo)
try:
await self.db.flush()
except IntegrityError:
raise HTTPException(
status_code=status.HTTP_409_CONFLICT,
detail=(
"No se puede eliminar el vehículo: tiene asignaciones de rutas "
"u otros registros vinculados."
),
) from None

# --- CÓDIGO NUEVO A USAR ---

async def eliminar_vehiculo(self, id_vehiculo: int) -> None:
"""
Elimina un vehículo de la BD local.

    Cambios:
    - Elimina en BD local primero
    - Luego sincroniza la eliminación con API externa
    """
    from services.external_sync_service import get_external_sync_service, SyncStatus

    vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
    id_externo = vehiculo.id_externo

    # 1. Eliminar de BD local
    await self.db.delete(vehiculo)
    try:
        await self.db.flush()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede eliminar el vehículo: tiene asignaciones de rutas "
                "u otros registros vinculados."
            ),
        ) from None

    # 2. Sincronizar eliminación con API externa
    if id_externo:
        sync_service = get_external_sync_service()
        if sync_service.es_sincronizacion_habilitada():
            try:
                metadata = await sync_service.sync_delete_vehiculo(
                    id_externo=id_externo,
                    recurso_id_local=id_vehiculo,
                )

                if metadata.estado != SyncStatus.SUCCESS:
                    logger.warning(
                        f"Vehículo {id_vehiculo} eliminado localmente pero "
                        f"sincronización falló: {metadata.error_message}"
                    )
            except Exception as e:
                logger.error(f"Error sincronizando eliminación de vehículo {id_vehiculo}: {e}")

# --- AGREGAR IMPORTS AL INICIO DEL ARCHIVO ---

# Agregar después de los otros imports:

from services.external_sync_service import get_external_sync_service, SyncStatus

# ============================================================================

# 2. MODIFICACIONES EN: services/service_posiciones.py

# ============================================================================

"""
CAMBIOS:

- Remover hardcoded perfil_id en registrar_posicion()
- Usar perfil_id dinámico desde config
- Usar ExternalSyncService para sincronización

NOTA: Ver la línea:
perfil_id="f105a9d3-13b3-4066-b5f7-edae6801e366" # ← HARDCODED ❌
"""

# --- CÓDIGO ORIGINAL A REEMPLAZAR ---

# En registrar_posicion(), la línea con hardcoded perfil_id:

if asignacion_externa and asignacion_externa.recorrido_externo_id:
api_service = APIExternaService()
await api_service.registrar_posicion_externa(
recorrido_externo_id=asignacion_externa.recorrido_externo_id,
latitud=float(data.latitud),
longitud=float(data.longitud),
perfil_id="f105a9d3-13b3-4066-b5f7-edae6801e366" # ← HARDCODED ❌
)

# --- CÓDIGO NUEVO A USAR ---

if asignacion_externa and asignacion_externa.recorrido_externo_id: # Usar servicio centralizado de sincronización
from services.external_sync_service import get_external_sync_service, SyncStatus

    sync_service = get_external_sync_service()
    if sync_service.es_sincronizacion_habilitada():
        metadata = await sync_service.sync_create_posicion(
            recorrido_externo_id=asignacion_externa.recorrido_externo_id,
            latitud=float(data.latitud),
            longitud=float(data.longitud),
            perfil_id=None,  # Usa el configurado por defecto
            recurso_id_local=posicion.id_posicion if hasattr(posicion, 'id_posicion') else None,
        )

        if metadata.estado != SyncStatus.SUCCESS:
            logger.warning(
                f"Posición registrada localmente pero sincronización falló: "
                f"{metadata.error_message}"
            )

# ============================================================================

# 3. MODIFICACIONES EN: services/service_asignacionrutas.py (Opcional)

# ============================================================================

"""
CAMBIOS RECOMENDADOS (no críticos):

- Usar ExternalSyncService en iniciar_recorrido_con_api_externa()
- Usar ExternalSyncService en finalizar_recorrido_con_api_externa()

IMPACTO: Centraliza la lógica y mejora el logging.
"""

# No es crítico cambiar estos métodos ahora, pero es recomendado para consistencia.

# ============================================================================

# RESUMEN DE CAMBIOS

# ============================================================================

"""
ARCHIVOS MODIFICADOS: 3

1. services/service_vehiculo.py
   - actualizar_vehiculo_por_id() → Agregado sincronización ✅
   - cambiar_estado_vehiculo() → Agregado sincronización ✅
   - eliminar_vehiculo() → Agregado sincronización ✅
   - Importar: ExternalSyncService, SyncStatus ✅

2. services/service_posiciones.py
   - registrar_posicion() → Remover hardcoded perfil_id ✅
   - registrar_posicion() → Usar ExternalSyncService ✅
   - Importar: ExternalSyncService, SyncStatus ✅

3. services/external_sync_service.py (NUEVO)
   - ✅ Crear archivo completo

CAMBIOS NO CRÍTICOS (Recomendados):

- services/service_asignacionrutas.py → Usar ExternalSyncService en iniciar/finalizar

ROUTERS (Sin cambios)

- Los routers NO necesitan cambios
- Los controladores NO necesitan cambios
- Todo ocurre en la capa de servicios
  """
