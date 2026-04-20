# schemas/schema_vehiculo.py

"""Schemas del módulo de vehículos.

Validan la entrada del CRUD y definen la estructura de salida del recurso.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from models.model_vehiculo import EstadoVehiculo
from fastapi import Form

class VehiculoCreate(BaseModel):
    placa: str = Field(
        ...,
        pattern=r"^[A-Z]{3}\d{3}$",
        description="Placa del vehículo (3 letras + 3 números, ej. ABC123)",
)
    modelo: Optional[str] = Field(None, max_length=50, description="Modelo del vehículo")
    capacidad_m3: Optional[float] = Field(None, gt=0, description="Capacidad del vehículo en metros cúbicos")
    estado: EstadoVehiculo = Field(EstadoVehiculo.disponible, description="Estado operativo del vehículo")

    @classmethod
    def as_form(
        cls,
        placa: str = Form(..., pattern=r"^[A-Z]{3}\d{3}$"),
        modelo: Optional[str] = Form(None),
        capacidad_m3: Optional[float] = Form(None),
        estado: EstadoVehiculo = Form(EstadoVehiculo.disponible),
    ):
        return cls(
            placa=placa,
            modelo=modelo,
            capacidad_m3=capacidad_m3,
            estado=estado,
        )

class VehiculoUpdate(BaseModel):
    placa:        Optional[str] = None
    modelo:       Optional[str] = None
    capacidad_m3: Optional[float] = None
    estado:       Optional[EstadoVehiculo] = None

    @classmethod
    def as_form(
        cls,
        placa: Optional[str] = Form(None),
        modelo: Optional[str] = Form(None),
        capacidad_m3: Optional[float] = Form(None),
        estado: Optional[EstadoVehiculo] = Form(None),
    ):
        return cls(
            placa=placa,
            modelo=modelo,
            capacidad_m3=capacidad_m3,
            estado=estado,
        )

class VehiculoResponse(BaseModel):
    id_vehiculo:  int
    id_externo:   Optional[str] = None
    placa:        str
    modelo:       Optional[str] = None
    capacidad_m3: Optional[float]
    estado:       EstadoVehiculo
    created_at:   datetime
    datos_api_externo: Optional[dict] = None

    model_config =  ConfigDict(from_attributes=True)