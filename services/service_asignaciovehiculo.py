# services/service_asignaciovehiculo.py

"""Servicios del módulo de asignaciones.

Aquí viven las reglas de negocio que conectan vehículos, rutas externas,
tripulación y eventos WebSocket del recorrido.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timezone
from models.model_asignacionvehiculo import AsignacionVehiculo, EstadoAsignacion
from models.model_vehiculo import Vehiculo, EstadoVehiculo
from schemas.schema_asignaciovehiculo import AsignacionCreate
from core.websocket_manager import ws_manager
from services.service_rutas_externo import RutasExternoService


class AsignacionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    def _con_relaciones(self):
        """Crea una consulta base con `vehiculo` y `tripulacion` precargados."""
        return (
            select(AsignacionVehiculo)
            .options(
                selectinload(AsignacionVehiculo.vehiculo),
                selectinload(AsignacionVehiculo.tripulacion),
            )
        )

    async def crear_asignacion(self, data: AsignacionCreate) -> AsignacionVehiculo:
        """Crea una asignación nueva si el vehículo existe y está disponible."""
        # Validar que la ruta existe en la API externa
        rutas_service = RutasExternoService()
        ruta_existe = await rutas_service.validar_ruta_existe(data.id_ruta)
        if not ruta_existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La ruta con id {data.id_ruta} no existe en el servicio de rutas.",
            )

        result = await self.db.execute(
            select(Vehiculo).where(Vehiculo.id_vehiculo == data.id_vehiculo)
        )
        vehiculo = result.scalar_one_or_none()
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el vehículo con id {data.id_vehiculo} para crear la asignación.",
            )
        if vehiculo.estado != EstadoVehiculo.disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El vehículo con id {data.id_vehiculo} no está disponible para asignación. Estado actual: {vehiculo.estado.value}.",
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
                detail=f"No se encontró la asignación con id {id_asignacion}.",
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
                detail=f"No se encontró la asignación con id {id_asignacion}.",
            )
        if asignacion.estado != EstadoAsignacion.pendiente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación {id_asignacion} no está en estado pendiente; solo en ese estado se puede modificar la tripulación.",
            )
        return asignacion

    async def iniciar_recorrido(self, id_asignacion: int) -> AsignacionVehiculo:
        """Inicia el recorrido una vez que toda la tripulación ha confirmado."""
        asignacion = await self.obtener_asignacion_id(id_asignacion) 
        if asignacion.estado != EstadoAsignacion.pendiente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación {id_asignacion} no se puede iniciar porque su estado actual es '{asignacion.estado.value}'.",
            )
        no_confirmados = [t for t in asignacion.tripulacion if not t.confirmado]
        if no_confirmados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede iniciar la asignación {id_asignacion}: faltan {len(no_confirmados)} integrante(s) por confirmar.",
            )
        # Una vez iniciada, la asignación cambia a `en_curso` y el vehículo queda `en_ruta`.
        asignacion.estado          = EstadoAsignacion.en_curso
        asignacion.hora_salida     = datetime.now(timezone.utc)
        asignacion.vehiculo.estado = EstadoVehiculo.en_ruta
        await self.db.flush()

        # Se notifica a los clientes suscritos mediante WebSocket.
        await ws_manager.broadcast(id_asignacion, {
            "evento":        "recorrido_iniciado",
            "id_asignacion": id_asignacion,
            "hora_salida":   asignacion.hora_salida.isoformat(),
            "estado":        asignacion.estado.value,
        })
        return asignacion

    async def finalizar_recorrido(self, id_asignacion: int) -> AsignacionVehiculo:
        """Finaliza un recorrido activo y devuelve el vehículo a disponibilidad."""
        asignacion = await self.obtener_asignacion_id(id_asignacion)
        if asignacion.estado != EstadoAsignacion.en_curso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación {id_asignacion} no se puede finalizar porque su estado actual es '{asignacion.estado.value}'.",
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
        """Cancela una asignación no completada y libera su vehículo."""
        asignacion = await self.obtener_asignacion_id(id_asignacion) 
        if asignacion.estado == EstadoAsignacion.completada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede cancelar la asignación {id_asignacion} porque ya fue completada.",
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

    async def obtener_detalles_ruta(self, id_ruta: int) -> dict | None:
        """Obtiene los detalles completos de una ruta desde la API externa."""
        rutas_service = RutasExternoService()
        return await rutas_service.obtener_ruta_por_id(id_ruta)