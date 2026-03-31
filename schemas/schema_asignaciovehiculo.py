from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from models.model_asignacionvehiculo import EstadoAsignacion
from schemas.schema_vehiculo import VehiculoResponse
from schemas.schema_tripulacionasignada import TripulacionResponse

class AsignacionCreate(BaseModel):
    id_vehiculo: int = Field(..., gt=0)
    id_ruta:     str = Field(..., min_length=1)
    fecha:       datetime = Field(..., description="Fecha de la asignación")

class AsignacionUpdate(BaseModel):
    estado:      EstadoAsignacion | None = None
    hora_salida: datetime         | None = None

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