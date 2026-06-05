# services/service_vehiculo.py

"""Servicios del módulo de vehículos.

Aquí se concentra la lógica del CRUD de camiones y el control de sus estados
operativos (`disponible`, `en_ruta`, `mantenimiento`, etc.).
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from models.model_vehiculo import Vehiculo, EstadoVehiculo
from schemas.schema_vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from services.service_api_externa import APIExternaService
from services.external_sync_service import get_external_sync_service, SyncStatus

logger = logging.getLogger(__name__)


def _id_desde_item_api(item: dict) -> str | None:
    for key in ("id", "vehiculo_id", "id_vehiculo"):
        v = item.get(key)
        if v is not None:
            return str(v)
    return None


class VehiculoService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def añadir_vehiculo(self, data: VehiculoCreate) -> Vehiculo:
        """Crea un vehículo nuevo verificando que la placa no esté repetida."""
        result = await self.db.execute(
            select(Vehiculo).where(Vehiculo.placa == data.placa)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un vehículo registrado con la placa '{data.placa}'.",
            )
        vehiculo = Vehiculo(**data.model_dump())
        self.db.add(vehiculo)
        await self.db.flush()

        # Sincronización robusta usando ExternalSyncService
        sync_service = get_external_sync_service()
        if sync_service.es_sincronizacion_habilitada():
            try:
                metadata = await sync_service.sync_create_vehiculo(
                    placa=vehiculo.placa,
                    marca=None,
                    modelo=vehiculo.modelo,
                    activo=vehiculo.estado != EstadoVehiculo.inactivo,
                    recurso_id_local=vehiculo.id_vehiculo,
                )
                if metadata.estado == SyncStatus.SUCCESS:
                    vehiculo.id_externo = metadata.id_externo
                else:
                    logger.warning(
                        f"[SYNC] Vehículo {vehiculo.placa} creado localmente pero la API externa rechazó la sincronización: {metadata.error_message}"
                    )
            except Exception as e:
                logger.error(
                    f"[SYNC ERROR] Error inesperado al intentar enviar vehículo {vehiculo.placa} a la API: {str(e)}"
                )
        else:
            logger.info(
                f"[SYNC] Sincronización deshabilitada para vehículo {vehiculo.placa}. Verifique RUTAS_API_URL y PERFIL_ID."
            )

        await self.db.flush()
        return vehiculo

    async def obtener_todos_vehiculos(self) -> list[VehiculoResponse]:
        result = await self.db.execute(select(Vehiculo))
        locales = list(result.scalars().all())
        externos: list[dict] = []
        try:
            externos = await APIExternaService().listar_vehiculos_externos()
        except HTTPException:
            pass
        por_id: dict[str, dict] = {}
        for item in externos:
            eid = _id_desde_item_api(item)
            if eid:
                por_id[eid] = item
        salida: list[VehiculoResponse] = []
        for v in locales:
            datos = por_id.get(v.id_externo) if v.id_externo else None
            base = VehiculoResponse.model_validate(v)
            salida.append(base.model_copy(update={"datos_api_externo": datos}))
        return salida

    async def _obtener_vehiculo_orm(self, id_vehiculo: int) -> Vehiculo:
        """Instancia ORM desde BD (para delete/update); no mezclar con VehiculoResponse."""
        result = await self.db.execute(
            select(Vehiculo).where(Vehiculo.id_vehiculo == id_vehiculo)
        )
        vehiculo = result.scalar_one_or_none()
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un vehículo con id {id_vehiculo}.",
            )
        return vehiculo

    async def obtener_vehiculo_por_id(self, id_vehiculo: int) -> VehiculoResponse:
        vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
        datos = None
        if vehiculo.id_externo:
            try:
                externos = await APIExternaService().listar_vehiculos_externos()
                for item in externos:
                    if _id_desde_item_api(item) == vehiculo.id_externo:
                        datos = item
                        break
            except HTTPException:
                pass
        base = VehiculoResponse.model_validate(vehiculo)
        return base.model_copy(update={"datos_api_externo": datos})

    async def actualizar_vehiculo_por_id(
        self, id_vehiculo: int, data: VehiculoUpdate
    ) -> VehiculoResponse:
        """Actualiza parcialmente los datos de un vehículo existente."""
        vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
        for campo, valor in data.model_dump(exclude_none=True).items():
            setattr(vehiculo, campo, valor)
        await self.db.flush()

        # Sincronizar con API externa si el vehículo tiene ID externo
        if vehiculo.id_externo:
            try:
                sync_service = get_external_sync_service()
                metadata = await sync_service.sync_update_vehiculo(
                    id_externo=vehiculo.id_externo,
                    placa=vehiculo.placa,
                    modelo=vehiculo.modelo,
                    activo=vehiculo.estado != EstadoVehiculo.inactivo,
                    recurso_id_local=id_vehiculo,
                )
                if metadata.estado != SyncStatus.SUCCESS:
                    logger.warning(
                        "Vehículo %s actualizado en BD local pero sincronización falló: %s",
                        id_vehiculo,
                        metadata.error_message,
                    )
            except Exception as e:
                logger.warning(
                    "Vehículo %s actualizado en BD local pero no se pudo sincronizar: %s",
                    id_vehiculo,
                    str(e),
                )
        await self.db.commit()

        await self.db.commit()
        return await self.obtener_vehiculo_por_id(id_vehiculo)

    async def cambiar_estado_vehiculo(
        self, id_vehiculo: int, estado: EstadoVehiculo
    ) -> VehiculoResponse:
        """Actualiza únicamente el estado operativo del vehículo."""
        vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
        vehiculo.estado = estado
        await self.db.flush()

        # Sincronizar con API externa si el vehículo tiene ID externo
        if vehiculo.id_externo:
            try:
                sync_service = get_external_sync_service()
                metadata = await sync_service.sync_update_vehiculo(
                    id_externo=vehiculo.id_externo,
                    activo=estado != EstadoVehiculo.inactivo,
                    recurso_id_local=id_vehiculo,
                )
                if metadata.estado != SyncStatus.SUCCESS:
                    logger.warning(
                        "Estado del vehículo %s actualizado en BD local pero sincronización falló: %s",
                        id_vehiculo,
                        metadata.error_message,
                    )
            except Exception as e:
                logger.warning(
                    "Estado del vehículo %s actualizado en BD local pero no se pudo sincronizar: %s",
                    id_vehiculo,
                    str(e),
                )

        await self.db.commit()
        return await self.obtener_vehiculo_por_id(id_vehiculo)

    async def eliminar_vehiculo(self, id_vehiculo: int) -> None:
        vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
        id_externo = vehiculo.id_externo  # Guardar antes de eliminar

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

        # Sincronizar eliminación con API externa si el vehículo tenía ID externo
        if id_externo:
            try:
                sync_service = get_external_sync_service()
                metadata = await sync_service.sync_delete_vehiculo(
                    id_externo=id_externo,
                    recurso_id_local=id_vehiculo,
                )
                if metadata.estado != SyncStatus.SUCCESS:
                    logger.warning(
                        "Vehículo %s eliminado de BD local pero sincronización falló: %s",
                        id_vehiculo,
                        metadata.error_message,
                    )
            except Exception as e:
                logger.warning(
                    "Vehículo %s eliminado de BD local pero no se pudo sincronizar eliminación: %s",
                    id_vehiculo,
                    str(e),
                )

    async def sincronizar_vehiculos_desde_api_externa(self) -> dict[str, int]:
        """
        Importa vehículos desde la API externa a la BD local con deduplicación.
        
        Returns:
            Dict con estadísticas: {'importados': int, 'existentes': int, 'errores': int}
        """
        try:
            # Obtener vehículos desde API externa
            externos = await APIExternaService().listar_vehiculos_externos()
            
            # Obtener vehículos existentes en BD local
            result = await self.db.execute(select(Vehiculo))
            locales = result.scalars().all()
            
            # Crear índices para deduplicación
            placas_locales = {v.placa for v in locales}
            ids_externos_locales = {v.id_externo for v in locales if v.id_externo}
            
            importados = 0
            existentes = 0
            errores = 0
            
            for veh_ext in externos:
                try:
                    # Extraer datos del vehículo externo
                    placa = veh_ext.get("placa")
                    id_externo = veh_ext.get("id")
                    modelo = veh_ext.get("modelo")
                    marca = veh_ext.get("marca")
                    activo = veh_ext.get("activo", True)
                    
                    if not placa or not id_externo:
                        logger.warning(f"Vehículo externo sin placa o id: {veh_ext}")
                        errores += 1
                        continue
                    
                    # Verificar duplicados por placa o id_externo
                    if placa in placas_locales or id_externo in ids_externos_locales:
                        existentes += 1
                        logger.info(f"Vehículo {placa} ya existe localmente, omitiendo")
                        continue
                    
                    # Determinar estado basado en 'activo'
                    estado = EstadoVehiculo.disponible if activo else EstadoVehiculo.inactivo
                    
                    # Crear vehículo local
                    nuevo_vehiculo = Vehiculo(
                        placa=placa,
                        modelo=modelo,
                        marca=marca,
                        estado=estado,
                        id_externo=id_externo,
                        capacidad_m3=10.0  # Valor por defecto ya que la API externa no lo tiene
                    )
                    
                    self.db.add(nuevo_vehiculo)
                    await self.db.flush()
                    
                    # Actualizar índices
                    placas_locales.add(placa)
                    ids_externos_locales.add(id_externo)
                    
                    importados += 1
                    logger.info(f"Vehículo {placa} importado desde API externa (ID externo: {id_externo})")
                    
                except Exception as e:
                    logger.error(f"Error importando vehículo {veh_ext}: {str(e)}")
                    errores += 1
            
            await self.db.commit()
            
            logger.info(
                f"Sincronización completada: {importados} importados, {existentes} existentes, {errores} errores"
            )
            
            return {
                "importados": importados,
                "existentes": existentes,
                "errores": errores
            }
            
        except HTTPException as e:
            logger.error(f"Error en sincronización: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado en sincronización: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en sincronización: {str(e)}"
            )
