# services/service_tripulacionasignada.py

"""Servicios del módulo de tripulación.

Se encarga de agregar integrantes, confirmar su participación y retirarlos
cuando la asignación todavía está en estado pendiente.
"""

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
        """Asegura que la asignación exista y aún pueda modificarse."""
        result = await self.db.execute(
            select(AsignacionVehiculo).where(
                AsignacionVehiculo.id_asignacion == id_asignacion
            )
        )
        asignacion = result.scalar_one_or_none()
        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la asignación {id_asignacion}.",
            )
        if asignacion.estado != EstadoAsignacion.pendiente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación {id_asignacion} no está pendiente; no se puede modificar su tripulación.",
            )
        return asignacion

    async def agregar_miembro(self, id_asignacion: int, data: TripulacionCreate) -> TripulacionAsignacion:
        """Agrega un integrante nuevo a la tripulación evitando duplicados."""
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
                detail=f"El usuario {data.id_usuario} ya pertenece a la asignación {id_asignacion}.",
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
        """Marca la participación del integrante como confirmada y emite un evento."""
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
                detail=f"El usuario {id_usuario} no pertenece a la asignación {id_asignacion}.",
            )
        if miembro.confirmado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El usuario {id_usuario} ya confirmó su participación en la asignación {id_asignacion}.",
            )

        # Se registra la confirmación y su marca temporal para trazabilidad operativa.
        miembro.confirmado    = True
        miembro.confirmado_at = datetime.now(timezone.utc)
        await self.db.flush()

        # El cambio se difunde en tiempo real a los clientes conectados.
        await ws_manager.broadcast(id_asignacion, {
            "evento":        "tripulacion_confirmo",
            "id_asignacion": id_asignacion,
            "id_usuario":    id_usuario,
            "rol":           miembro.rol_tripulacion.value,
        })
        return miembro

    async def eliminar_miembro_asignacion(self, id_asignacion: int, id_usuario: int):
        """Elimina un miembro de la tripulación si la asignación sigue abierta a cambios."""
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
                detail=f"No se encontró al usuario {id_usuario} dentro de la tripulación de la asignación {id_asignacion}.",
            )
        await self.db.delete(miembro)
        await self.db.flush()
        