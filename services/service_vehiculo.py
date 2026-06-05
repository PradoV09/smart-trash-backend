# services/service_vehiculo.py

"""Servicios del módulo de vehículos.

Aquí se concentra la lógica del CRUD de camiones y el control de sus estados
operativos (`disponible`, `en_ruta`, `mantenimiento`, etc.).
"""

import logging
import traceback

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
        # Excluir marca del modelo (no está en la BD)
        vehiculo_data = data.model_dump(exclude={'marca'})
        vehiculo = Vehiculo(**vehiculo_data)
        self.db.add(vehiculo)
        await self.db.flush()

        logger.info(f"[DEBUG] Vehículo creado localmente: id={vehiculo.id_vehiculo}, placa={vehiculo.placa}")

        # ====================================================================
        # SINCRONIZACIÓN CON API EXTERNA
        # Estrategia: intentar con ExternalSyncService primero (payload con
        # campos activo/marca/modelo). Si falla, usar APIExternaService como
        # fallback (payload con estado/placa/modelo/capacidad_m3/perfil_id).
        # ====================================================================
        sync_exitoso = False
        sync_service = get_external_sync_service()

        logger.info(f"[DEBUG] sync_service creado, verificando si está habilitada...")
        habilitada = sync_service.es_sincronizacion_habilitada()
        logger.info(f"[DEBUG] es_sincronizacion_habilitada() = {habilitada}")

        if habilitada:
            # --- Intento 1: ExternalSyncService ---
            try:
                logger.info(
                    f"[SYNC] Intentando sincronizar vehículo {vehiculo.placa} "
                    f"(id_local={vehiculo.id_vehiculo}) con ExternalSyncService..."
                )
                metadata = await sync_service.sync_create_vehiculo(
                    placa=vehiculo.placa,
                    modelo=vehiculo.modelo,
                    activo=vehiculo.estado != EstadoVehiculo.inactivo,
                    recurso_id_local=vehiculo.id_vehiculo,
                )
                if metadata.estado == SyncStatus.SUCCESS:
                    vehiculo.id_externo = metadata.id_externo
                    sync_exitoso = True
                    logger.info(
                        f"[SYNC ✅] Vehículo {vehiculo.placa} sincronizado exitosamente. "
                        f"id_externo={metadata.id_externo}"
                    )
                else:
                    logger.warning(
                        f"[SYNC ⚠️] ExternalSyncService falló para {vehiculo.placa}: "
                        f"{metadata.error_message} (code={metadata.error_code})"
                    )
            except Exception as e:
                logger.error(
                    f"[SYNC ❌] ExternalSyncService excepción para {vehiculo.placa}: {e}\n"
                    f"{traceback.format_exc()}"
                )

            # --- Intento 2 (fallback): APIExternaService ---
            if not sync_exitoso:
                try:
                    logger.info(
                        f"[SYNC FALLBACK] Intentando con APIExternaService para {vehiculo.placa}..."
                    )
                    api_ext = APIExternaService()
                    ext_id, resp_json = await api_ext.crear_vehiculo_externo(
                        placa=vehiculo.placa,
                        modelo=vehiculo.modelo,
                        capacidad_m3=vehiculo.capacidad_m3,
                        estado=vehiculo.estado,
                    )
                    vehiculo.id_externo = ext_id
                    sync_exitoso = True
                    logger.info(
                        f"[SYNC FALLBACK ✅] Vehículo {vehiculo.placa} sincronizado vía fallback. "
                        f"id_externo={ext_id}, respuesta={resp_json}"
                    )
                except Exception as e2:
                    logger.error(
                        f"[SYNC FALLBACK ❌] APIExternaService también falló para {vehiculo.placa}: {e2}\n"
                        f"{traceback.format_exc()}"
                    )

            if not sync_exitoso:
                logger.error(
                    f"[SYNC FINAL ❌] Vehículo {vehiculo.placa} creado en BD local "
                    f"pero NO se pudo sincronizar con la API externa por ningún método."
                )
        else:
            logger.info(
                f"[SYNC SKIP] Sincronización deshabilitada para vehículo {vehiculo.placa}. "
                f"Verifique RUTAS_API_URL y PERFIL_ID en .env"
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
            # No incluir marca en la respuesta (frontend no la usa)
            vehiculo_dict = {
                "id_vehiculo": v.id_vehiculo,
                "id_externo": v.id_externo,
                "placa": v.placa,
                "modelo": v.modelo,
                "capacidad_m3": v.capacidad_m3,
                "estado": v.estado,
                "created_at": v.created_at,
                "datos_api_externo": datos,
            }
            base = VehiculoResponse(**vehiculo_dict)
            salida.append(base)
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
        # No incluir marca en la respuesta (frontend no la usa)
        vehiculo_dict = {
            "id_vehiculo": vehiculo.id_vehiculo,
            "id_externo": vehiculo.id_externo,
            "placa": vehiculo.placa,
            "modelo": vehiculo.modelo,
            "capacidad_m3": vehiculo.capacidad_m3,
            "estado": vehiculo.estado,
            "created_at": vehiculo.created_at,
            "datos_api_externo": datos,
        }
        return VehiculoResponse(**vehiculo_dict)

    async def actualizar_vehiculo_por_id(
        self, id_vehiculo: int, data: VehiculoUpdate
    ) -> VehiculoResponse:
        """Actualiza parcialmente los datos de un vehículo existente."""
        vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
        for campo, valor in data.model_dump(exclude_none=True).items():
            setattr(vehiculo, campo, valor)
        await self.db.flush()

        # Sincronizar con API externa
        sync_service = get_external_sync_service()
        if sync_service.es_sincronizacion_habilitada():
            # Si el vehículo local no tiene id_externo, intentamos crearlo en la API externa primero
            if not vehiculo.id_externo:
                try:
                    logger.info(
                        f"[SYNC] El vehículo {id_vehiculo} ({vehiculo.placa}) no tiene id_externo. "
                        f"Intentando crear en la API externa..."
                    )
                    metadata = await sync_service.sync_create_vehiculo(
                        placa=vehiculo.placa,
                        marca=vehiculo.marca,
                        modelo=vehiculo.modelo,
                        activo=vehiculo.estado != EstadoVehiculo.inactivo,
                        recurso_id_local=id_vehiculo,
                    )
                    if metadata.estado == SyncStatus.SUCCESS:
                        vehiculo.id_externo = metadata.id_externo
                        logger.info(
                            f"[SYNC ✅] Vehículo {id_vehiculo} creado exitosamente en la API externa desde actualización."
                        )
                except Exception as e:
                    logger.warning(
                        f"[SYNC ❌] Error al intentar crear vehículo {id_vehiculo} desde actualización: {e}"
                    )

            if vehiculo.id_externo:
                try:
                    logger.info(
                        f"[SYNC] Actualizando vehículo {id_vehiculo} (ext={vehiculo.id_externo}) en API externa..."
                    )
                    metadata = await sync_service.sync_update_vehiculo(
                        id_externo=vehiculo.id_externo,
                        placa=vehiculo.placa,
                        modelo=vehiculo.modelo,
                        activo=vehiculo.estado != EstadoVehiculo.inactivo,
                        recurso_id_local=id_vehiculo,
                    )
                    if metadata.estado == SyncStatus.SUCCESS:
                        logger.info(
                            f"[SYNC ✅] Vehículo {id_vehiculo} actualizado en API externa."
                        )
                    else:
                        logger.warning(
                            "[SYNC ⚠️] Vehículo %s actualizado en BD local pero sincronización falló: %s",
                            id_vehiculo,
                            metadata.error_message,
                        )
                except Exception as e:
                    logger.warning(
                        "[SYNC ❌] Vehículo %s actualizado en BD local pero no se pudo sincronizar: %s",
                        id_vehiculo,
                        str(e),
                    )
        else:
            logger.info(
                f"[SYNC SKIP] Sincronización deshabilitada para vehículo {id_vehiculo}."
            )

        await self.db.flush()
        return await self.obtener_vehiculo_por_id(id_vehiculo)

    async def cambiar_estado_vehiculo(
        self, id_vehiculo: int, estado: EstadoVehiculo
    ) -> VehiculoResponse:
        """Actualiza únicamente el estado operativo del vehículo."""
        vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
        vehiculo.estado = estado
        await self.db.flush()

        # Sincronizar con API externa
        sync_service = get_external_sync_service()
        if sync_service.es_sincronizacion_habilitada():
            # Si el vehículo local no tiene id_externo, intentamos crearlo en la API externa primero
            if not vehiculo.id_externo:
                try:
                    logger.info(
                        f"[SYNC] El vehículo {id_vehiculo} ({vehiculo.placa}) no tiene id_externo. "
                        f"Intentando crear en la API externa..."
                    )
                    metadata = await sync_service.sync_create_vehiculo(
                        placa=vehiculo.placa,
                        marca=vehiculo.marca,
                        modelo=vehiculo.modelo,
                        activo=estado != EstadoVehiculo.inactivo,
                        recurso_id_local=id_vehiculo,
                    )
                    if metadata.estado == SyncStatus.SUCCESS:
                        vehiculo.id_externo = metadata.id_externo
                        logger.info(
                            f"[SYNC ✅] Vehículo {id_vehiculo} creado exitosamente en la API externa desde cambio de estado."
                        )
                except Exception as e:
                    logger.warning(
                        f"[SYNC ❌] Error al intentar crear vehículo {id_vehiculo} desde cambio de estado: {e}"
                    )

            if vehiculo.id_externo:
                try:
                    metadata = await sync_service.sync_update_vehiculo(
                        id_externo=vehiculo.id_externo,
                        placa=vehiculo.placa,
                        modelo=vehiculo.modelo,
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
        placa = vehiculo.placa

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
                logger.info(
                    f"[SYNC] Eliminando vehículo {placa} (ext={id_externo}) de API externa..."
                )
                metadata = await sync_service.sync_delete_vehiculo(
                    id_externo=id_externo,
                    recurso_id_local=id_vehiculo,
                )
                if metadata.estado == SyncStatus.SUCCESS:
                    logger.info(
                        f"[SYNC ✅] Vehículo {placa} eliminado de API externa."
                    )
                else:
                    logger.warning(
                        "[SYNC ⚠️] Vehículo %s eliminado de BD local pero sincronización falló: %s",
                        id_vehiculo,
                        metadata.error_message,
                    )
            except Exception as e:
                logger.warning(
                    "[SYNC ❌] Vehículo %s eliminado de BD local pero no se pudo sincronizar eliminación: %s",
                    id_vehiculo,
                    str(e),
                )
        else:
            logger.info(
                f"[SYNC SKIP] Vehículo {id_vehiculo} ({placa}) no tenía id_externo, no se sincroniza delete."
            )
