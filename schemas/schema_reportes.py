from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReporteCreate(BaseModel):
    id_usuario:    int | None = None
    u_gmail_cache: str | None = None
    u_rol_cache:   str | None = None
    descripcion:   str
    asunto:        str
    evidencia_url: str | None = None

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