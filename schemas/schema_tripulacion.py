# schemas/schema_tripulacion.py

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from models.model_asignaciontripulacion import RolTripulacion
from schemas.schema_usuarios import UsuarioResponse

class TripulacionMiembroCreate(BaseModel):
    id_usuario: int = Field(..., gt=0)
    rol_tripulacion: RolTripulacion

class TripulacionMiembroResponse(BaseModel):
    id: int
    id_usuario: int
    rol_tripulacion: RolTripulacion
    usuario: UsuarioResponse

    model_config = ConfigDict(from_attributes=True)

class TripulacionCreate(BaseModel):
    nombre: str | None = None
    miembros: list[TripulacionMiembroCreate] = Field(..., min_length=4, max_length=4)

class TripulacionResponse(BaseModel):
    id_tripulacion: int
    nombre: str | None
    created_at: datetime
    miembros: list[TripulacionMiembroResponse]

    model_config = ConfigDict(from_attributes=True)
