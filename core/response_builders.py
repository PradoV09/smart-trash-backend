"""Helpers para construir respuestas exitosas con un formato uniforme."""

from __future__ import annotations

from typing import Any


def success_response(*, data: Any = None, message: str = "Operación completada correctamente.") -> dict[str, Any]:
    """Devuelve una respuesta estándar de éxito para toda la API."""
    return {
        "success": True,
        "message": message,
        "data": data,
    }
