"""Servicio para estado en vivo de asignaciones (admin)."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional

from models.model_asignacionrutas import AsignacionRutas, EstadoAsignacion
from models.model_posiciones import RecorridoPosicion
from models.model_tripulacion import Tripulacion, TripulacionMiembro
from models.model_usuarios import Usuario
from schemas.schema_estado_vivo import (
    EstadoVivoResponse,
    UbicacionActual,
    MiembroTripulacionInfo,
)


class EstadoVivoService:
    """Servicio para obtener el estado en vivo de una asignación."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtener_estado_vivo(
        self,
        id_asignacion: int,
    ) -> EstadoVivoResponse:
        """Obtiene el estado completo en vivo de una asignación."""
        # Obtener asignación con relaciones
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
        
        # Obtener última posición
        ubicacion_actual = await self._obtener_ultima_posicion(id_asignacion)
        
        # Obtener información de tripulación
        miembros = await self._obtener_miembros_tripulacion(asignacion.id_tripulacion)
        
        # Calcular tiempo transcurrido
        tiempo_transcurrido = None
        if asignacion.hora_salida and asignacion.estado == EstadoAsignacion.en_curso:
            ahora = datetime.now(timezone.utc)
            if asignacion.hora_salida.tzinfo is None:
                asignacion.hora_salida = asignacion.hora_salida.replace(tzinfo=timezone.utc)
            tiempo_transcurrido = int((ahora - asignacion.hora_salida).total_seconds())
        
        # Calcular distancia recorrida
        distancia_recorrida = await self._calcular_distancia_recorrida(id_asignacion)
        
        return EstadoVivoResponse(
            id_asignacion=id_asignacion,
            estado=asignacion.estado,
            ubicacion_actual=ubicacion_actual,
            ultimo_hito=None,  # Por implementar con API externa
            miembros_tripulacion=miembros,
            hora_salida=asignacion.hora_salida,
            tiempo_transcurrido=tiempo_transcurrido,
            distancia_recorrida=distancia_recorrida,
            ultima_actualizacion=datetime.now(timezone.utc),
        )

    async def _obtener_ultima_posicion(
        self,
        id_asignacion: int,
    ) -> Optional[UbicacionActual]:
        """Obtiene la última posición registrada."""
        result = await self.db.execute(
            select(RecorridoPosicion)
            .where(RecorridoPosicion.id_asignacion == id_asignacion)
            .order_by(desc(RecorridoPosicion.timestamp))
            .limit(1)
        )
        posicion = result.scalar_one_or_none()
        
        if posicion:
            return UbicacionActual(
                latitud=posicion.latitud,
                longitud=posicion.longitud,
                timestamp=posicion.timestamp,
                accuracy=posicion.accuracy,
                speed=posicion.speed,
                bearing=posicion.bearing,
            )
        return None

    async def _obtener_miembros_tripulacion(
        self,
        id_tripulacion: int | None,
    ) -> list[MiembroTripulacionInfo]:
        """Obtiene los miembros de la tripulación."""
        if not id_tripulacion:
            return []
        
        result = await self.db.execute(
            select(TripulacionMiembro)
            .where(TripulacionMiembro.id_tripulacion == id_tripulacion)
            .options(
                select(TripulacionMiembro.usuario)
            )
        )
        miembros = result.scalars().all()
        
        resultado = []
        for miembro in miembros:
            # Cargar usuario
            await self.db.refresh(miembro, ["usuario"])
            resultado.append(
                MiembroTripulacionInfo(
                    id_usuario=miembro.usuario.id_usuario,
                    nombre=miembro.usuario.nombre,
                    rol_tripulacion=miembro.rol_tripulacion.value,
                    confirmado=miembro.confirmado,
                )
            )
        
        return resultado

    async def _calcular_distancia_recorrida(
        self,
        id_asignacion: int,
    ) -> Optional[float]:
        """Calcula la distancia total recorrida en kilómetros.
        
        Implementación simple: suma de distancias entre posiciones consecutivas.
        En producción usar el algoritmo de Haversine.
        """
        result = await self.db.execute(
            select(RecorridoPosicion)
            .where(RecorridoPosicion.id_asignacion == id_asignacion)
            .order_by(RecorridoPosicion.timestamp)
        )
        posiciones = result.scalars().all()
        
        if len(posiciones) < 2:
            return None
        
        distancia_total = 0.0
        
        for i in range(1, len(posiciones)):
            pos_actual = posiciones[i]
            pos_anterior = posiciones[i - 1]
            
            # Distancia simple (en producción usar Haversine)
            distancia_total += ((pos_actual.latitud - pos_anterior.latitud) ** 2 + 
                              (pos_actual.longitud - pos_anterior.longitud) ** 2) ** 0.5
        
        # Convertir a kilómetros (aproximado)
        return round(distancia_total * 111.0, 2)