# services/asignacion_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timezone
from models.model_asignacionvehiculo import AsignacionVehiculo, EstadoAsignacion
from models.model_vehiculo import Vehiculo, EstadoVehiculo
from schemas.schema_asignaciovehiculo import AsignacionCreate
from core.websocket_manager import ws_manager

class AsignacionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    def _con_relaciones(self):
        return (
            select(AsignacionVehiculo)
            .options(
                selectinload(AsignacionVehiculo.vehiculo),
                selectinload(AsignacionVehiculo.tripulacion),
            )
        )

    async def crear_asignacion(self, data: AsignacionCreate) -> AsignacionVehiculo:
        result = await self.db.execute(
            select(Vehiculo).where(Vehiculo.id_vehiculo == data.id_vehiculo)
        )
        vehiculo = result.scalar_one_or_none()
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehículo no encontrado",
            )
        if vehiculo.estado != EstadoVehiculo.disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El vehículo no está disponible, estado actual: {vehiculo.estado}",
            )
        asignacion = AsignacionVehiculo(**data.model_dump())
        self.db.add(asignacion)
        await self.db.flush()
        return asignacion

    async def obtener_asignaciones(self) -> list[AsignacionVehiculo]:
        result = await self.db.execute(self._con_relaciones())
        return result.scalars().all()

    async def obtener_asignacion_id(self, id_asignacion: int) -> AsignacionVehiculo:
        result = await self.db.execute(
            self._con_relaciones().where(
                AsignacionVehiculo.id_asignacion == id_asignacion
            )
        )
        asignacion = result.scalar_one_or_none()
        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignación no encontrada",
            )
        return asignacion

    async def obtener_asignacion_ruta(self, id_ruta: str) -> AsignacionVehiculo | None:
        result = await self.db.execute(
            self._con_relaciones().where(
                AsignacionVehiculo.id_ruta == id_ruta
            )
        )
        return result.scalar_one_or_none()

    async def verificar_asignacion_pendiente(self, id_asignacion: int) -> AsignacionVehiculo:
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

    async def iniciar_recorrido(self, id_asignacion: int) -> AsignacionVehiculo:
        asignacion = await self.obtener_asignacion_id(id_asignacion) 
        if asignacion.estado != EstadoAsignacion.pendiente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede iniciar una asignación en estado pendiente",
            )
        no_confirmados = [t for t in asignacion.tripulacion if not t.confirmado]
        if no_confirmados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Toda la tripulación debe confirmar antes de iniciar",
            )
        asignacion.estado          = EstadoAsignacion.en_curso
        asignacion.hora_salida     = datetime.now(timezone.utc)
        asignacion.vehiculo.estado = EstadoVehiculo.en_ruta
        await self.db.flush()

        await ws_manager.broadcast(id_asignacion, {
            "evento":        "recorrido_iniciado",
            "id_asignacion": id_asignacion,
            "hora_salida":   asignacion.hora_salida.isoformat(),
            "estado":        asignacion.estado.value,
        })
        return asignacion

    async def finalizar_recorrido(self, id_asignacion: int) -> AsignacionVehiculo:
        asignacion = await self.obtener_asignacion_id(id_asignacion)
        if asignacion.estado != EstadoAsignacion.en_curso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede finalizar una asignación en curso",
            )
        asignacion.estado          = EstadoAsignacion.completada
        asignacion.vehiculo.estado = EstadoVehiculo.disponible
        await self.db.flush()

        await ws_manager.broadcast(id_asignacion, {
            "evento":        "recorrido_finalizado",
            "id_asignacion": id_asignacion,
            "estado":        asignacion.estado.value,
        })
        return asignacion

    async def cancelar_asignacion(self, id_asignacion: int) -> AsignacionVehiculo:
        asignacion = await self.obtener_asignacion_id(id_asignacion) 
        if asignacion.estado == EstadoAsignacion.completada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cancelar una asignación ya completada",
            )
        asignacion.estado          = EstadoAsignacion.cancelada
        asignacion.vehiculo.estado = EstadoVehiculo.disponible
        await self.db.flush()

        await ws_manager.broadcast(id_asignacion, {
            "evento":        "asignacion_cancelada",
            "id_asignacion": id_asignacion,
            "estado":        asignacion.estado.value,
        })
        return asignacion