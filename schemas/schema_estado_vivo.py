"""Schemas para el estado en vivo de una asignación (admin)."""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from models.model_asignacionrutas import EstadoAsignacion


class UbicacionActual(BaseModel):
    """Última ubicación conocida del vehículo."""
    
    latitud: float
    longitud: float
    timestamp: datetime
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None


class MiembroTripulacionInfo(BaseModel):
    """Información de un miembro de la tripulación."""
    
    id_usuario: int
    nombre: str
    rol_tripulacion: str
    confirmado: bool


class EstadoVivoResponse(BaseModel):
    """Response completo del estado en vivo de una asignación."""
    
    id_asignacion: int = Field(..., description="ID de la asignación")
    estado: EstadoAsignacion = Field(..., description="Estado actual del recorrido")
    ubicacion_actual: Optional[UbicacionActual] = Field(
        None,
        description="Última posición reportada"
    )
    ultimo_hito: Optional[str] = Field(
        None,
        description="Último hito alcanzado en la ruta"
    )
    miembros_tripulacion: list[MiembroTripulacionInfo] = Field(
        ...,
        description="Miembros de la tripulación"
    )
    hora_salida: Optional[datetime] = Field(
        None,
        description="Hora de inicio del recorrido"
    )
    tiempo_transcurrido: Optional[int] = Field(
        None,
        description="Tiempo transcurrido en segundos desde el inicio"
    )
    distancia_recorrida: Optional[float] = Field(
        None,
        description="Distancia total recorrida en kilómetros"
    )
    ultima_actualizacion: datetime = Field(
        ...,
        description="Timestamp de la última actualización"
    )

    model_config = ConfigDict(from_attributes=True)


class EstadoVivoWebSocket(BaseModel):
    """Schema para eventos WebSocket de estado vivo."""
    
    evento: str = Field(..., description="Tipo de evento")
    id_asignacion: int
    data: EstadoVivoResponse
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp del evento"
    )