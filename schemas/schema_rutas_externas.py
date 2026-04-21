"""Schemas para endpoints de rutas contra API externa."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RutasCreateRequest(BaseModel):
    nombre_ruta: str = Field(..., min_length=1, max_length=255)
    perfil_id: UUID
    calles_ids: list[UUID] | None = None
    shape: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_calles_or_shape(self) -> "RutasCreateRequest":
        has_calles = bool(self.calles_ids)
        has_shape = self.shape is not None
        if has_calles == has_shape:
            raise ValueError(
                "Debes enviar exactamente uno de estos campos: 'calles_ids' o 'shape'."
            )
        return self


class RutasCreateResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

class RutaResponse(BaseModel):
    id: UUID
    perfil_id: UUID
    nombre_ruta: str
    color_hex: str | None = None
    shape: Any | None = None
    created_at: str | None = None
    updated_at: str | None = None
    model_config = ConfigDict(extra="allow")
