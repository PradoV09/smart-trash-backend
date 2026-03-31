# schemas/schema_tripulacionasignada.py

"""Schemas del módulo de tripulación asignada."""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from models.model_tripulacionasignacion import RolTripulacion
from schemas.schema_usuarios import UsuarioResponse

class TripulacionCreate(BaseModel):
    id_usuario:      int = Field(..., gt=0)
    rol_tripulacion: RolTripulacion = Field(..., description="Rol del tripulante en la asignación")

class TripulacionResponse(BaseModel):
    id:              int
    id_asignacion:   int
    id_usuario:      int
    rol_tripulacion: RolTripulacion
    confirmado:      bool
    confirmado_at:   datetime | None
    usuario:         UsuarioResponse

    model_config = ConfigDict(from_attributes=True)