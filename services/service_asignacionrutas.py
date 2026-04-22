# services/service_asignaciovehiculo.py

"""Servicios del módulo de asignaciones.

Aquí viven las reglas de negocio que conectan vehículos, rutas externas,
tripulación y eventos WebSocket del recorrido.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Any
from fastapi import HTTPException, status
from datetime import datetime, timezone
from models.model_asignacionrutas import AsignacionRutas, EstadoAsignacion
from models.model_asignaciontripulacion import TripulacionAsignacion
from models.model_tripulacion import Tripulacion, TripulacionMiembro
from models.model_vehiculo import Vehiculo, EstadoVehiculo
from schemas.schema_asignacionrutas import AsignacionCreate
from core.websocket_manager import ws_manager
from services.service_api_externa import APIExternaService
from models.model_usuarios import Usuario


class AsignacionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    def _con_relaciones(self):
        """Crea una consulta base con `vehiculo` y `tripulacion` precargados."""
        return (
            select(AsignacionRutas)
            .options(
                selectinload(AsignacionRutas.vehiculo),
                selectinload(AsignacionRutas.tripulacion).selectinload(Tripulacion.miembros).selectinload(TripulacionMiembro.usuario).selectinload(Usuario.perfil),
                selectinload(AsignacionRutas.tripulacion).selectinload(Tripulacion.miembros).selectinload(TripulacionMiembro.usuario).selectinload(Usuario.rol),
            )
        )

    async def crear_asignacion(self, data: AsignacionCreate) -> AsignacionRutas:
        """Crea una asignación nueva vinculando vehículo y tripulación."""
        # 1. Validar Ruta (con fallback por si falla el fetch individual de la API externa)
        api_service = APIExternaService()
        ruta_valida = False
        try:
            await api_service.obtener_ruta(data.id_ruta)
            ruta_valida = True
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(status_code=400, detail=f"Ruta {data.id_ruta} no encontrada.")
            
            # Fallback: Intentar buscar en la lista completa si el fetch individual falla (500 o similar)
            try:
                resp = await api_service.listar_rutas()
                rutas = resp.get("data", []) if isinstance(resp, dict) else resp
                if any(r.get("id") == data.id_ruta for r in rutas):
                    ruta_valida = True
            except Exception:
                # Si fallan ambos, pero el error original fue un 500 de la API externa,
                # para no bloquear al usuario si la API es inestable, podríamos dejarlo pasar
                # pero es mejor ser estrictos o registrar el error.
                pass
            
            if not ruta_valida:
                raise e # Re-lanzar el error original si el fallback también falló o no encontró la ruta

        # 2. Validar Vehículo
        res_v = await self.db.execute(select(Vehiculo).where(Vehiculo.id_vehiculo == data.id_vehiculo))
        vehiculo = res_v.scalar_one_or_none()
        if not vehiculo or vehiculo.estado != EstadoVehiculo.disponible:
            raise HTTPException(status_code=400, detail="Vehículo no disponible.")

        # 3. Validar Tripulación (Nuevo)
        from models.model_tripulacion import Tripulacion
        res_t = await self.db.execute(select(Tripulacion).where(Tripulacion.id_tripulacion == data.id_tripulacion))
        if not res_t.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Tripulación no encontrada.")

        asignacion = AsignacionRutas(**data.model_dump())
        self.db.add(asignacion)
        await self.db.flush()
        return await self.obtener_asignacion_id(asignacion.id_asignacion)

    async def obtener_asignaciones(self) -> list[AsignacionRutas]:
        result = await self.db.execute(self._con_relaciones())
        return result.scalars().all()

    async def obtener_asignacion_id(self, id_asignacion: int) -> AsignacionRutas:
        result = await self.db.execute(
            self._con_relaciones().where(
                AsignacionRutas.id_asignacion == id_asignacion
            )
        )
        asignacion = result.scalar_one_or_none()
        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la asignación con id {id_asignacion}.",
            )
        return asignacion

    async def obtener_asignacion_ruta(self, id_ruta: str) -> AsignacionRutas | None:
        result = await self.db.execute(
            self._con_relaciones().where(
                AsignacionRutas.id_ruta == id_ruta
            )
        )
        return result.scalar_one_or_none()

    async def verificar_asignacion_pendiente(self, id_asignacion: int) -> AsignacionRutas:
        result = await self.db.execute(
            select(AsignacionRutas).where(
                AsignacionRutas.id_asignacion == id_asignacion
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

    async def iniciar_recorrido(self, id_asignacion: int) -> AsignacionRutas:
        """Inicia el recorrido una vez que toda la tripulación ha confirmado."""
        asignacion = await self.obtener_asignacion_id(id_asignacion) 
        if asignacion.estado != EstadoAsignacion.pendiente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación {id_asignacion} no se puede iniciar porque su estado actual es '{asignacion.estado.value}'.",
            )

        # Regla de Negocio: Validar estructura obligatoria (1 conductor + 3 recolectores)
        from services.service_asignaciontripulacion import TripulacionService
        trip_service = TripulacionService(self.db)
        if not await trip_service.validar_tripulacion(id_asignacion):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede iniciar la asignación {id_asignacion}: la tripulación no cumple "
                       "la estructura reglamentaria obligatoria (1 conductor y 3 recolectores)."
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

    async def finalizar_recorrido(self, id_asignacion: int) -> AsignacionRutas:
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

    async def cancelar_asignacion(self, id_asignacion: int) -> AsignacionRutas:
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

    async def obtener_detalles_ruta(self, id_ruta: str) -> dict | None:
        """Obtiene los detalles completos de una ruta desde la API externa."""
        api_service = APIExternaService()
        try:
            return await api_service.obtener_ruta(id_ruta)
        except HTTPException:
            # Fallback: buscar en la lista
            try:
                resp = await api_service.listar_rutas()
                rutas = resp.get("data", []) if isinstance(resp, dict) else resp
                for r in rutas:
                    if r.get("id") == id_ruta:
                        return r
            except Exception:
                pass
            return None