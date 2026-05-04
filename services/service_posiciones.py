"""Servicio para gestión de posiciones GPS del recorrido."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional

from models.model_posiciones import RecorridoPosicion
from models.model_asignacionrutas import AsignacionRutas, EstadoAsignacion
from schemas.schema_posiciones import (
    PosicionCreate,
    PosicionResponse,
    PosicionListResponse,
)
from core.websocket_manager import ws_manager
import logging

from models.model_asignacion_externa import AsignacionExterna
from services.service_api_externa import APIExternaService

logger = logging.getLogger(__name__)


class PosicionesService:
    """Servicio para gestionar posiciones GPS."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _validar_asignacion_en_curso(
        self,
        id_asignacion: int,
        id_usuario: int | None = None
    ) -> AsignacionRutas:
        """Valida que la asignación exista y esté en curso."""
        result = await self.db.execute(
            select(AsignacionRutas).where(
                AsignacionRutas.id_asignacion == id_asignacion
            )
        )
        asignacion = result.scalar_one_or_none()
        
        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la asignación con id {id_asignacion}."
            )
        
        if asignacion.estado != EstadoAsignacion.en_curso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación {id_asignacion} no está en curso. "
                       f"Estado actual: {asignacion.estado.value}"
            )
        
        return asignacion

    async def registrar_posicion(
        self,
        id_asignacion: int,
        data: PosicionCreate,
    ) -> PosicionResponse:
        """Registra una nueva posición GPS."""
        # Validar asignación
        await self._validar_asignacion_en_curso(id_asignacion)
        
        # Crear posición
        posicion = RecorridoPosicion(
            id_asignacion=id_asignacion,
            latitud=data.latitud,
            longitud=data.longitud,
            accuracy=data.accuracy,
            speed=data.speed,
            bearing=data.bearing,
            timestamp=data.timestamp,
        )
        
        self.db.add(posicion)
        await self.db.flush()
        await self.db.refresh(posicion)
        
        # Notificar por WebSocket a los administradores
        await ws_manager.broadcast(id_asignacion, {
            "evento": "posicion_actualizada",
            "id_asignacion": id_asignacion,
            "latitud": float(data.latitud),
            "longitud": float(data.longitud),
            "timestamp": data.timestamp.isoformat(),
            "data": { # Respaldo para compatibilidad
                "lat": float(data.latitud),
                "lon": float(data.longitud)
            }
        })
        
        # Enviar posición a la API externa
        try:
            result_ext = await self.db.execute(
                select(AsignacionExterna).where(AsignacionExterna.id_asignacion == id_asignacion)
            )
            asignacion_externa = result_ext.scalar_one_or_none()
            
            if asignacion_externa and asignacion_externa.recorrido_externo_id:
                api_service = APIExternaService()
                await api_service.registrar_posicion_externa(
                    recorrido_externo_id=asignacion_externa.recorrido_externo_id,
                    latitud=float(data.latitud),
                    longitud=float(data.longitud),
                    perfil_id="f105a9d3-13b3-4066-b5f7-edae6801e366"
                )
        except Exception as e:
            logger.error(f"Error al reenviar posición a la API externa para asignación {id_asignacion}: {str(e)}")
            # No lanzamos excepción para no romper el flujo principal si la API externa falla
        
        return PosicionResponse.model_validate(posicion)

    async def listar_posiciones(
        self,
        id_asignacion: int,
        page: int = 1,
        page_size: int = 50,
    ) -> PosicionListResponse:
        """Lista posiciones con paginación."""
        # Validar que la asignación exista
        result = await self.db.execute(
            select(AsignacionRutas).where(
                AsignacionRutas.id_asignacion == id_asignacion
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la asignación con id {id_asignacion}."
            )
        
        # Contar total
        count_result = await self.db.execute(
            select(func.count()).select_from(RecorridoPosicion).where(
                RecorridoPosicion.id_asignacion == id_asignacion
            )
        )
        total = count_result.scalar() or 0
        
        # Calcular paginación
        offset = (page - 1) * page_size
        has_next = (offset + page_size) < total
        has_prev = page > 1
        
        # Obtener posiciones
        result = await self.db.execute(
            select(RecorridoPosicion)
            .where(RecorridoPosicion.id_asignacion == id_asignacion)
            .order_by(desc(RecorridoPosicion.timestamp))
            .offset(offset)
            .limit(page_size)
        )
        posiciones = result.scalars().all()
        
        return PosicionListResponse(
            items=[PosicionResponse.model_validate(p) for p in posiciones],
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_prev=has_prev,
        )

    async def obtener_ultima_posicion(
        self,
        id_asignacion: int,
    ) -> Optional[PosicionResponse]:
        """Obtiene la última posición registrada."""
        result = await self.db.execute(
            select(RecorridoPosicion)
            .where(RecorridoPosicion.id_asignacion == id_asignacion)
            .order_by(desc(RecorridoPosicion.timestamp))
            .limit(1)
        )
        posicion = result.scalar_one_or_none()
        
        if posicion:
            return PosicionResponse.model_validate(posicion)
        return None