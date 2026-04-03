# schemas/schema_tripulacionasignada.py

"""Schemas del módulo de tripulación asignada."""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from models.model_tripulacionasignacion import RolTripulacion
from schemas.schema_usuarios import UsuarioResponse
from fastapi import Form

class TripulacionCreate(BaseModel):
    id_usuario:      int = Field(..., gt=0)
    rol_tripulacion: RolTripulacion = Field(..., description="Rol del tripulante en la asignación")

    @classmethod
    def as_form(
        cls,
        id_usuario: int = Form(..., gt=0),
        rol_tripulacion: RolTripulacion = Form(...),
    ):
        return cls(
            id_usuario=id_usuario,
            rol_tripulacion=rol_tripulacion,
        )

class TripulacionResponse(BaseModel):
    id:              int
    id_asignacion:   int
    id_usuario:      int
    rol_tripulacion: RolTripulacion
    confirmado:      bool
    confirmado_at:   datetime | None
    usuario:         UsuarioResponse

    model_config = ConfigDict(from_attributes=True)