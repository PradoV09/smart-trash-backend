"""Schemas del módulo de reportes.

Definen el payload de entrada para registrar actividad y la estructura de salida.
"""

from typing import Optional, List

from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from fastapi import Form

class ReporteCreate(BaseModel):
    id_usuario:    int | None = None
    u_gmail_cache: str | None = None
    u_rol_cache:   str | None = None
    descripcion:   str
    asunto:        str
    evidencia_url: str | None = None
    latitud:       float | None = None
    longitud:      float | None = None

    @classmethod
    def as_form(
        cls,
        id_usuario: Optional[int] = Form(None),
        u_gmail_cache: Optional[str] = Form(None),
        u_rol_cache: Optional[str] = Form(None),
        descripcion: str = Form(...),
        asunto: str = Form(...),
        evidencia_url: Optional[str] = Form(None),
        latitud: Optional[float] = Form(None),
        longitud: Optional[float] = Form(None),
    ):
        return cls(
            id_usuario=id_usuario,
            u_gmail_cache=u_gmail_cache,
            u_rol_cache=u_rol_cache,
            descripcion=descripcion,
            asunto=asunto,
            evidencia_url=evidencia_url,
            latitud=latitud,
            longitud=longitud,
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
    latitud:       float | None = None
    longitud:      float | None = None
    
    # Campos virtuales calculados
    terminado: bool = False
    notas_terminacion: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def compute_virtual_fields(self) -> 'ReporteResponse':
        if self.descripcion and "[TERMINADO:" in self.descripcion:
            self.terminado = True
            if "]" in self.descripcion:
                parts = self.descripcion.split("]", 1)
                if len(parts) > 1:
                    self.notas_terminacion = parts[1].strip()
        return self


# Schema para crear reportes como conductor con fotos y prioridad
class ReporteDriverCreate(BaseModel):
    asunto: str
    descripcion: str
    estado: str  # baja, media, alta
    fotos: Optional[List[dict]] = None  # Array de fotos en base64
    id_asignacion: Optional[int] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

# Response para conductores (adaptado al modelo real)
class ReporteDriverResponse(BaseModel):
    id_registro: int
    asunto: str
    descripcion: str
    fecha: datetime
    id_usuario: Optional[int] = None
    u_gmail_cache: Optional[str] = None
    u_rol_cache: Optional[str] = None  # Aquí guardamos el estado como workaround
    evidencia_url: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    # Campos virtuales para mantener compatibilidad con la API
    estado: Optional[str] = None  # Se extraerá de u_rol_cache
    terminado: Optional[bool] = False  # Se detectará de la descripción
    fotos: Optional[List[dict]] = None

    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_reporte_actividad(cls, reporte: 'ReporteActividad'):
        """Crea response desde ReporteActividad extrayendo estado y terminado."""
        # Extraer estado de u_rol_cache
        estado = reporte.u_rol_cache if reporte.u_rol_cache in ['baja', 'media', 'alta'] else None
        
        # Detectar si está terminado por la descripción
        terminado = '[TERMINADO:' in reporte.descripcion if reporte.descripcion else False
        
        return cls(
            id_registro=reporte.id_registro,
            asunto=reporte.asunto,
            descripcion=reporte.descripcion,
            fecha=reporte.fecha,
            id_usuario=reporte.id_usuario,
            u_gmail_cache=reporte.u_gmail_cache,
            u_rol_cache=reporte.u_rol_cache,
            evidencia_url=reporte.evidencia_url,
            latitud=reporte.latitud,
            longitud=reporte.longitud,
            estado=estado,
            terminado=terminado
        )

# Schema para marcar reporte como terminado
class ReporteTerminadoUpdate(BaseModel):
    notas_terminacion: str

    @classmethod
    def as_form(
        cls,
        notas_terminacion: str = Form(..., description="Notas finales del reporte"),
    ):
        return cls(notas_terminacion=notas_terminacion)