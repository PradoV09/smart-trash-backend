"""Schemas del módulo de asignaciones.

Representan la entrada para crear asignaciones y las respuestas detalladas
para administración y consulta ciudadana.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from models.model_asignacionvehiculo import EstadoAsignacion
from schemas.schema_vehiculo import VehiculoResponse
from schemas.schema_tripulacionasignada import TripulacionResponse
from fastapi import Form

class AsignacionCreate(BaseModel):
    id_vehiculo: int = Field(..., gt=0)
    id_ruta:     str = Field(..., min_length=1)
    fecha:       datetime = Field(..., description="Fecha de la asignación")

    @classmethod
    def as_form(
        cls,
        id_vehiculo: int = Form(..., gt=0),
        id_ruta: str = Form(..., min_length=1),
        fecha: datetime = Form(...),
    ):
        return cls(
            id_vehiculo=id_vehiculo,
            id_ruta=id_ruta,
            fecha=fecha,
        )

class AsignacionUpdate(BaseModel):
    estado:      EstadoAsignacion | None = None
    hora_salida: datetime         | None = None

    @classmethod
    def as_form(
        cls,
        estado: Optional[EstadoAsignacion] = Form(None),
        hora_salida: Optional[datetime] = Form(None),
    ):
        return cls(
            estado=estado,
            hora_salida=hora_salida,
        )

class AsignacionResponse(BaseModel):
    id_asignacion: int
    id_vehiculo:   int
    id_ruta:       str
    fecha:         datetime
    hora_salida:   datetime | None
    estado:        EstadoAsignacion
    created_at:    datetime
    vehiculo:      VehiculoResponse
    tripulacion:   list[TripulacionResponse]

    model_config = ConfigDict(from_attributes=True)

# Solo para la app del ciudadano
class AsignacionPublicResponse(BaseModel):
    id_ruta:     str
    id_vehiculo: int
    hora_salida: datetime | None
    estado:      EstadoAsignacion

    model_config = ConfigDict(from_attributes=True)