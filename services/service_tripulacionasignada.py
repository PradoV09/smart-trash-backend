# services/tripulacion_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from models.model_tripulacionasignacion import TripulacionAsignacion
from models.model_asignacionvehiculo import AsignacionVehiculo, EstadoAsignacion
from schemas.schema_tripulacionasignada import TripulacionCreate
from core.websocket_manager import ws_manager  # ✅ para el broadcast de confirmación

class TripulacionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _verificar_asignacion_pendiente(self, id_asignacion: int) -> AsignacionVehiculo:
        result = await self.db.execute(
            select(AsignacionVehiculo).where(
                AsignacionVehiculo.id_asignacion == id_asignacion
            )
        )
        asignacion = result.scalar_one_or_none()
        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignación no encontrada",
            )
        if asignacion.estado != EstadoAsignacion.pendiente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede modificar la tripulación de una asignación pendiente",
            )
        return asignacion

    async def agregar_miembro(self, id_asignacion: int, data: TripulacionCreate) -> TripulacionAsignacion:
        await self._verificar_asignacion_pendiente(id_asignacion)

        result = await self.db.execute(
            select(TripulacionAsignacion).where(
                TripulacionAsignacion.id_asignacion == id_asignacion,
                TripulacionAsignacion.id_usuario    == data.id_usuario,
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya está en esta asignación",
            )

        miembro = TripulacionAsignacion(
            id_asignacion=id_asignacion,
            id_usuario=data.id_usuario,
            rol_tripulacion=data.rol_tripulacion,
        )
        self.db.add(miembro)
        await self.db.flush()
        return miembro

    async def confirmar_asignacion(self, id_asignacion: int, id_usuario: int) -> TripulacionAsignacion:
        result = await self.db.execute(
            select(TripulacionAsignacion).where(
                TripulacionAsignacion.id_asignacion == id_asignacion,
                TripulacionAsignacion.id_usuario    == id_usuario,
            )
        )
        miembro = result.scalar_one_or_none()
        if not miembro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No perteneces a esta asignación",
            )
        if miembro.confirmado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya confirmaste tu participación",
            )

        miembro.confirmado    = True
        miembro.confirmado_at = datetime.now(timezone.utc)
        await self.db.flush()

        await ws_manager.broadcast(id_asignacion, {
            "evento":        "tripulacion_confirmo",
            "id_asignacion": id_asignacion,
            "id_usuario":    id_usuario,
            "rol":           miembro.rol_tripulacion.value,
        })
        return miembro

    async def eliminar_miembro_asignacion(self, id_asignacion: int, id_usuario: int):
        await self._verificar_asignacion_pendiente(id_asignacion)

        result = await self.db.execute(
            select(TripulacionAsignacion).where(
                TripulacionAsignacion.id_asignacion == id_asignacion,
                TripulacionAsignacion.id_usuario    == id_usuario,
            )
        )
        miembro = result.scalar_one_or_none()
        if not miembro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Miembro no encontrado en la tripulación",
            )
        await self.db.delete(miembro)
        await self.db.flush()
        