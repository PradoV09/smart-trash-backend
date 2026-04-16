"""Schemas para reportes públicos de ciudadanos.

Permiten a usuarios no autenticados reportar problemas de recolección.
"""

from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from fastapi import Form
from typing import Optional


class ReportePublicoCreate(BaseModel):
    """Schema para crear un reporte público de ciudadano."""
    nombre: str
    correo: EmailStr
    descripcion: str
    asunto: str
    evidencia_url: str | None = None

    @classmethod
    def as_form(
        cls,
        nombre: str = Form(..., description="Nombre del ciudadano"),
        correo: str = Form(..., description="Correo electrónico de contacto"),
        descripcion: str = Form(..., description="Descripción detallada del problema"),
        asunto: str = Form(..., description="Asunto del reporte"),
        evidencia_url: Optional[str] = Form(None, description="URL de evidencia (foto/video)"),
    ):
        return cls(
            nombre=nombre,
            correo=correo,
            descripcion=descripcion,
            asunto=asunto,
            evidencia_url=evidencia_url,
        )


class ReportePublicoResponse(BaseModel):
    """Schema de respuesta para reportes públicos."""
    id_registro: int
    nombre: str
    correo: str
    descripcion: str
    asunto: str
    evidencia_url: str | None
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
