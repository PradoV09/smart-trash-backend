"""Schemas para endpoints de recorridos contra API externa."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IniciarRecorridoRequest(BaseModel):
    ruta_id: UUID = Field(..., description="UUID de la ruta en la API externa.")
    vehiculo_id: UUID = Field(..., description="UUID del vehiculo asignado al recorrido.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ruta_id": "550e8400-e29b-41d4-a716-446655440000",
                "vehiculo_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
            }
        }
    )


class RegistrarPosicionRequest(BaseModel):
    lat: float = Field(..., description="Latitud GPS en formato decimal.")
    lon: float = Field(..., description="Longitud GPS en formato decimal.")
    perfil_id: UUID = Field(
        ...,
        description="UUID del perfil que envía la coordenada.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lat": 3.42158,
                "lon": -76.5205,
                "perfil_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        }
    )


class RecorridoResponse(BaseModel):
    model_config = ConfigDict(extra="allow")


class PosicionesRecorridoResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
