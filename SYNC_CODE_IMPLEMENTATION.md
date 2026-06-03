"""
CÓDIGO LISTO PARA COPIAR Y PEGAR

Este archivo contiene el código actualizado para los servicios que necesitan
sincronización bidireccional con la API externa.

INSTRUCCIONES:

1. Copiar el contenido de cada sección a los archivos indicados
2. Mantener los imports existentes
3. Agregar solo los imports nuevos indicados
4. Guardar y probar cada cambio

================================================================================
ARCHIVO 1: services/service_vehiculo.py
================================================================================
"""

# AGREGAR ESTOS IMPORTS AL INICIO (después de los imports existentes)

# =========================================================================

from services.external_sync_service import (
get_external_sync_service,
SyncStatus,
)

# REEMPLAZAR MÉTODO: actualizar_vehiculo_por_id

# =========================================================================

async def actualizar_vehiculo_por_id(self, id_vehiculo: int, data: VehiculoUpdate) -> VehiculoResponse:
"""Actualiza parcialmente los datos de un vehículo existente.

    ✨ NUEVO COMPORTAMIENTO:
    - Actualiza BD local primero (garantizado)
    - Sincroniza con API externa (best effort)
    - Si API externa falla, mantiene datos locales y registra error
    """
    vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)

    # 1. ACTUALIZAR EN BD LOCAL PRIMERO
    datos_actualizacion = data.model_dump(exclude_none=True)
    for campo, valor in datos_actualizacion.items():
        setattr(vehiculo, campo, valor)
    await self.db.flush()

    # 2. SINCRONIZAR CON API EXTERNA (si existe y está configurada)
    if vehiculo.id_externo:
        sync_service = get_external_sync_service()
        if sync_service.es_sincronizacion_habilitada():
            try:
                metadata = await sync_service.sync_update_vehiculo(
                    id_externo=vehiculo.id_externo,
                    placa=vehiculo.placa if "placa" in datos_actualizacion else None,
                    modelo=vehiculo.modelo if "modelo" in datos_actualizacion else None,
                    capacidad_m3=vehiculo.capacidad_m3 if "capacidad_m3" in datos_actualizacion else None,
                    recurso_id_local=id_vehiculo,
                )

                # Loguear resultado
                if metadata.estado != SyncStatus.SUCCESS:
                    logger.warning(
                        f"Vehículo {id_vehiculo} ({vehiculo.placa}) actualizado localmente. "
                        f"Sin embargo, sincronización con API externa falló: {metadata.error_message}"
                    )
            except Exception as e:
                logger.error(
                    f"Error inesperado sincronizando actualización de vehículo {id_vehiculo}: {e}"
                )

    return await self.obtener_vehiculo_por_id(id_vehiculo)

# REEMPLAZAR MÉTODO: cambiar_estado_vehiculo

# =========================================================================

async def cambiar_estado_vehiculo(self, id_vehiculo: int, estado: EstadoVehiculo) -> VehiculoResponse:
"""Actualiza únicamente el estado operativo del vehículo.

    ✨ NUEVO COMPORTAMIENTO:
    - Cambia estado en BD local primero
    - Sincroniza cambio con API externa
    - Si sincronización falla, mantiene cambio local
    """
    vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
    vehiculo.estado = estado
    await self.db.flush()

    # SINCRONIZAR CAMBIO DE ESTADO CON API EXTERNA
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
                        f"Vehículo {id_vehiculo} cambió estado a '{estado.value}' localmente. "
                        f"Sincronización con API externa falló: {metadata.error_message}"
                    )
            except Exception as e:
                logger.error(
                    f"Error sincronizando cambio de estado de vehículo {id_vehiculo}: {e}"
                )

    return await self.obtener_vehiculo_por_id(id_vehiculo)

# REEMPLAZAR MÉTODO: eliminar_vehiculo

# =========================================================================

async def eliminar_vehiculo(self, id_vehiculo: int) -> None:
"""Elimina un vehículo de la BD local y API externa.

    ✨ NUEVO COMPORTAMIENTO:
    - Elimina de BD local primero (garantizado)
    - Sincroniza eliminación con API externa (best effort)
    - Si sincronización falla, mantiene eliminación local
    """
    vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
    id_externo = vehiculo.id_externo
    placa = vehiculo.placa

    # 1. ELIMINAR DE BD LOCAL
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

    # 2. SINCRONIZAR ELIMINACIÓN CON API EXTERNA
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
                        f"Vehículo {placa} ({id_vehiculo}) eliminado localmente. "
                        f"Sin embargo, fallo la sincronización con API externa: {metadata.error_message}"
                    )
            except Exception as e:
                logger.error(
                    f"Error sincronizando eliminación de vehículo {id_vehiculo}: {e}"
                )

# TAMBIÉN MEJORAR: método añadir_vehiculo (opcional pero recomendado)

# =========================================================================

# CAMBIAR DE:

# ext*id, * = await APIExternaService().crear_vehiculo_externo(...)

# A:

# metadata = await sync_service.sync_create_vehiculo(

# placa=vehiculo.placa,

# modelo=vehiculo.modelo,

# capacidad_m3=vehiculo.capacidad_m3,

# estado=vehiculo.estado.value,

# recurso_id_local=vehiculo.id_vehiculo

# )

# if metadata.estado == SyncStatus.SUCCESS:

# vehiculo.id_externo = metadata.id_externo

# """

# ARCHIVO 2: services/service_posiciones.py

"""

# AGREGAR ESTOS IMPORTS AL INICIO

# =========================================================================

from services.external_sync_service import (
get_external_sync_service,
SyncStatus,
)

# BUSCAR Y REEMPLAZAR: En método registrar_posicion(), la sección:

# BUSCAR ESTA LÍNEA (contiene hardcoded perfil_id):

# =========================================================================

            if asignacion_externa and asignacion_externa.recorrido_externo_id:
                api_service = APIExternaService()
                await api_service.registrar_posicion_externa(
                    recorrido_externo_id=asignacion_externa.recorrido_externo_id,
                    latitud=float(data.latitud),
                    longitud=float(data.longitud),
                    perfil_id="f105a9d3-13b3-4066-b5f7-edae6801e366"  # ← HARDCODED ❌
                )

# REEMPLAZAR POR ESTO:

# =========================================================================

            if asignacion_externa and asignacion_externa.recorrido_externo_id:
                sync_service = get_external_sync_service()
                if sync_service.es_sincronizacion_habilitada():
                    try:
                        metadata = await sync_service.sync_create_posicion(
                            recorrido_externo_id=asignacion_externa.recorrido_externo_id,
                            latitud=float(data.latitud),
                            longitud=float(data.longitud),
                            perfil_id=None,  # Usa el configurado por defecto desde settings
                            recurso_id_local=posicion.id_posicion if hasattr(posicion, 'id_posicion') else None,
                        )

                        if metadata.estado != SyncStatus.SUCCESS:
                            logger.warning(
                                f"Posición registrada en asignación {id_asignacion} pero "
                                f"sincronización con API externa falló: {metadata.error_message}"
                            )
                    except Exception as e:
                        logger.error(
                            f"Error sincronizando posición en asignación {id_asignacion}: {e}"
                        )

# """

# ARCHIVO 3: core/dependecies.py (OPCIONAL pero RECOMENDADO)

Agregar esta dependencia para inyectar el servicio de sincronización en
controladores si lo necesitas en el futuro:
"""

async def get_external_sync_service() -> ExternalSyncService:
"""Dependencia para inyectar el servicio de sincronización."""
from services.external_sync_service import get_external_sync_service
return get_external_sync_service()

# """

# ARCHIVO 4: main.py o core/settings.py

PASO OPCIONAL: Agregar validación de configuración de API externa al iniciar
"""

async def verificar_config_api_externa():
"""Verifica que la API externa esté configurada."""
from services.external_sync_service import get_external_sync_service
sync_service = get_external_sync_service()
if not sync_service.es_sincronizacion_habilitada():
logger.warning(
"⚠️ API EXTERNA NO CONFIGURADA\n"
" Sincronización bidireccional deshabilitada.\n"
" Configura RUTAS_API_URL y PERFIL_ID en .env para habilitar."
)
else:
logger.info("✅ API Externa configurada - Sincronización bidireccional habilitada")

# Agregar a lifespan startup

# En main.py, en la función lifespan, agregar:

await verificar_config_api_externa()

# """

# VERIFICACIÓN DESPUÉS DE LOS CAMBIOS

Checklist de pruebas:

1. CREAR VEHÍCULO
   ✓ POST /admin/vehiculos
   ✓ Debe crear en BD local
   ✓ Debe crear en API externa
   ✓ Verificar que id_externo se guardó

2. ACTUALIZAR VEHÍCULO
   ✓ PATCH /admin/vehiculos/{id}
   ✓ Debe actualizar en BD local
   ✓ Debe actualizar en API externa
   ✓ Verificar logs de sincronización

3. CAMBIAR ESTADO VEHÍCULO
   ✓ PATCH /admin/vehiculos/{id}/estado
   ✓ Debe cambiar en BD local
   ✓ Debe cambiar en API externa

4. ELIMINAR VEHÍCULO
   ✓ DELETE /admin/vehiculos/{id}
   ✓ Debe eliminar de BD local
   ✓ Debe eliminar de API externa

5. REGISTRAR POSICIÓN
   ✓ POST /driver/asignaciones/{id}/posiciones
   ✓ Debe registrar en BD local
   ✓ Debe registrar en API externa
   ✓ Verificar que NO usa hardcoded perfil_id

6. ESCENARIOS DE ERROR
   ✓ Si API externa está down, operaciones locales aún funcionan
   ✓ Los errores se loguean correctamente
   ✓ Revisar logs en nivel WARNING/ERROR

================================================================================
ROLLBACK (si necesitas revertir)
================================================================================

Si necesitas revertir estos cambios:

1. Recuperar las versiones originales de:
   - services/service_vehiculo.py
   - services/service_posiciones.py

2. Eliminar:
   - services/external_sync_service.py

3. Remover imports de ExternalSyncService

Pero se recomienda MANTENER los cambios y usar el nuevo servicio.
"""
