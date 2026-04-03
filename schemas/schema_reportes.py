"""Schemas del módulo de reportes.

Definen el payload de entrada para registrar actividad y la estructura de salida.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from fastapi import Form

class ReporteCreate(BaseModel):
    id_usuario:    int | None = None
    u_gmail_cache: str | None = None
    u_rol_cache:   str | None = None
    descripcion:   str
    asunto:        str
    evidencia_url: str | None = None

    @classmethod
    def as_form(
        cls,
        id_usuario: Optional[int] = Form(None),
        u_gmail_cache: Optional[str] = Form(None),
        u_rol_cache: Optional[str] = Form(None),
        descripcion: str = Form(...),
        asunto: str = Form(...),
        evidencia_url: Optional[str] = Form(None),
    ):
        return cls(
            id_usuario=id_usuario,
            u_gmail_cache=u_gmail_cache,
            u_rol_cache=u_rol_cache,
            descripcion=descripcion,
            asunto=asunto,
            evidencia_url=evidencia_url,
        )

class ReporteResponse(BaseModel):
    id_registro:   int
    id_usuario:    int | None
    u_gmail_cache: str | None
    u_rol_cache:   str | None
    descripcion:   str
    asunto:        str
    evidencia_url: str | None
    fecha:         datetime

    model_config = ConfigDict(from_attributes=True)