"""Schemas para validación de fotos/evidencia del recorrido."""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
import re


class FotoCreate(BaseModel):
    """Schema para recibir una nueva foto del driver."""
    
    imagen_base64: str = Field(
        ...,
        min_length=1,
        description="Imagen en formato base64 con prefijo de MIME type"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp del dispositivo cuando se capturó la foto"
    )
    tipo: str = Field(
        ...,
        pattern="^(recoleccion|incidencia|cumplimiento)$",
        description="Tipo de foto: recoleccion, incidencia o cumplimiento"
    )

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "imagen_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
            "timestamp": "2026-04-23T10:30:00Z",
            "tipo": "recoleccion"
        }
    })

    @classmethod
    def validate_imagen_base64(cls, v: str) -> str:
        """Valida que el string base64 contenga un prefijo de imagen válido."""
        # Patrón para validar formato data URL de imagen
        pattern = r'^data:image/[a-z]+;base64,'
        if not re.match(pattern, v):
            raise ValueError(
                "El formato de imagen debe ser 'data:image/<tipo>;base64,<datos>' "
                "(ej: data:image/jpeg;base64,...)"
            )
        return v


class FotoResponse(BaseModel):
    """Schema para retornar una foto almacenada."""
    
    id: int = Field(..., description="ID único de la foto")
    id_asignacion: int = Field(..., description="ID de la asignación asociada")
    url: str = Field(..., description="URL de acceso a la imagen")
    tipo: str = Field(..., description="Tipo de foto")
    timestamp_captura: datetime
    timestamp_envio: datetime
    metadata: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FotoListResponse(BaseModel):
    """Schema para listar fotos de una asignación."""
    
    items: list[FotoResponse]
    total: int = Field(..., description="Total de fotos")