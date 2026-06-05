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

        # ====================================================================
        # ENVIAR VEHÍCULO NUEVO A API EXTERNA
        # ====================================================================
        sync_service = get_external_sync_service()

        if sync_service.es_sincronizacion_habilitada():
            try:
                logger.info(
                    f"[SYNC] Enviando vehículo {vehiculo.placa} a API externa..."
                )
                metadata = await sync_service.sync_create_vehiculo(
                    placa=vehiculo.placa,
                    marca=data.marca,
                    modelo=vehiculo.modelo,
                    activo=vehiculo.estado != EstadoVehiculo.inactivo,
                    recurso_id_local=vehiculo.id_vehiculo,
                )
                if metadata.estado == SyncStatus.SUCCESS:
                    vehiculo.id_externo = metadata.id_externo
                    logger.info(
                        f"[SYNC ✅] Vehículo {vehiculo.placa} enviado a API externa. "
                        f"id_externo={metadata.id_externo}"
                    )
                else:
                    logger.warning(
                        f"[SYNC ⚠️] Falló enviar vehículo {vehiculo.placa} a API externa: "
                        f"{metadata.error_message}"
                    )
            except Exception as e:
                logger.error(
                    f"[SYNC ❌] Error al enviar vehículo {vehiculo.placa} a API externa: {e}"
                )
        else:
            logger.info(
                f"[SYNC SKIP] Envío a API externa deshabilitado para vehículo {vehiculo.placa}."
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
        await self.db.commit()
        return await self.obtener_vehiculo_por_id(id_vehiculo)

    async def cambiar_estado_vehiculo(
        self, id_vehiculo: int, estado: EstadoVehiculo
    ) -> VehiculoResponse:
        """Actualiza únicamente el estado operativo del vehículo."""
        vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)
        vehiculo.estado = estado
        await self.db.commit()
        return await self.obtener_vehiculo_por_id(id_vehiculo)

    async def eliminar_vehiculo(self, id_vehiculo: int) -> None:
        vehiculo = await self._obtener_vehiculo_orm(id_vehiculo)

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
