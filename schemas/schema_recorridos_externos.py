"""Schemas para endpoints de recorridos contra API externa."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IniciarRecorridoRequest(BaseModel):
    ruta_id: UUID
    vehiculo_id: UUID


class RegistrarPosicionRequest(BaseModel):
    lat: float
    lon: float


class RecorridoResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
