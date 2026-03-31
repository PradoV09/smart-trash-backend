# schemas/schema_vehiculo.py

"""Schemas del módulo de vehículos.

Validan la entrada del CRUD y definen la estructura de salida del recurso.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from models.model_vehiculo import EstadoVehiculo

class VehiculoCreate(BaseModel):
    placa:        str = Field(..., min_length=6, max_length=10, description="Placa del vehículo")
    modelo:       str   | None = None
    capacidad_m3: float | None = None
    estado:       EstadoVehiculo = EstadoVehiculo.disponible

class VehiculoUpdate(BaseModel):
    placa:        str          | None = None
    modelo:       str          | None = None
    capacidad_m3: float        | None = None
    estado:       EstadoVehiculo | None = None

class VehiculoResponse(BaseModel):
    id_vehiculo:  int
    placa:        str
    modelo:       str   | None
    capacidad_m3: float | None
    estado:       EstadoVehiculo
    created_at:   datetime

    model_config =  ConfigDict(from_attributes=True)