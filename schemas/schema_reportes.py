from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ReporteCreate(BaseModel):
    id_usuario: Optional[int] = Field(None, description="ID del usuario si está autenticado")
    u_gmail_cache: Optional[str] = Field(None, max_length=100, description="Correo del usuario al momento del reporte")
    descripcion: str = Field(..., description="Descripción del reporte")
    asunto: str = Field(..., max_length=100, description="Asunto del reporte")
    evidencia_url: Optional[str] = Field(None, max_length=255, description="URL de la evidencia")
    u_rol_cache: Optional[str] = Field(None, max_length=20, description="Rol del usuario al momento del reporte")

class ResponseReporte(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_registro: int
    descripcion: str
    asunto: str
    fecha: datetime
    evidencia_url: Optional[str] = None
    u_gmail_cache: Optional[str] = None
    u_rol_cache: Optional[str] = None