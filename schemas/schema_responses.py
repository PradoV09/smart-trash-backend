# schemas/schema_responses.py

"""Schemas reutilizables para respuestas estándar de la API."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Wrapper uniforme para respuestas exitosas."""

    success: bool = True
    message: str  = "OK"  # ✅ default para no obligar a pasarlo siempre
    data:    T


class ErrorDetailPayload(BaseModel):
    """Detalle interno del objeto de error."""

    code:      str
    message:   str
    details:   Any = None
    path:      str
    method:    str
    timestamp: str


class ErrorResponse(BaseModel):
    """Wrapper uniforme para respuestas de error."""

    success: bool             = False
    error:   ErrorDetailPayload

SuccessResponse.model_rebuild()