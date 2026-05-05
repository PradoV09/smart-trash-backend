"""Schemas para validación de posiciones GPS durante el recorrido."""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class PosicionCreate(BaseModel):
    """Schema para recibir una nueva posición del driver."""
    
    latitud: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitud en grados decimales"
    )
    longitud: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitud en grados decimales"
    )
    accuracy: Optional[float] = Field(
        None,
        ge=0,
        le=1000,
        description="Precisión de la ubicación en metros"
    )
    speed: Optional[float] = Field(
        None,
        ge=0,
        le=500,
        description="Velocidad del vehículo en km/h"
    )
    bearing: Optional[float] = Field(
        None,
        ge=0,
        le=360,
        description="Dirección del movimiento en grados (0-360)"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp del dispositivo móvil cuando se capturó la posición"
    )

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "latitud": 3.8801,
            "longitud": -77.0188,
            "accuracy": 5.2,
            "speed": 25.3,
            "bearing": 45.5,
            "timestamp": "2026-04-23T10:30:00Z"
        }
    })


class PosicionResponse(BaseModel):
    """Schema para retornar una posición almacenada."""
    
    id: int = Field(..., description="ID único de la posición")
    id_asignacion: int = Field(..., description="ID de la asignación asociada")
    latitud: float
    longitud: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None
    timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PosicionListResponse(BaseModel):
    """Schema para listar posiciones con paginación."""
    
    items: list[PosicionResponse]
    total: int = Field(..., description="Total de posiciones")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    has_next: bool = Field(..., description="Hay más páginas")
    has_prev: bool = Field(..., description="Hay página anterior")