# core/error_handlers.py

"""Manejadores globales de errores para responder con un formato uniforme.

Este módulo centraliza la estructura JSON de errores para que el frontend,
el equipo de desarrollo y futuras integraciones reciban respuestas consistentes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _status_to_code(status_code: int) -> str:
    """Mapea códigos HTTP a identificadores semánticos estables."""
    mapping = {
        status.HTTP_400_BAD_REQUEST:           "bad_request",
        status.HTTP_401_UNAUTHORIZED:          "unauthorized",
        status.HTTP_403_FORBIDDEN:             "forbidden",
        status.HTTP_404_NOT_FOUND:             "not_found",
        status.HTTP_405_METHOD_NOT_ALLOWED:    "method_not_allowed",
        status.HTTP_409_CONFLICT:              "conflict",
        status.HTTP_422_UNPROCESSABLE_CONTENT: "validation_error",  # ✅ corregido
        status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_server_error",
    }
    return mapping.get(status_code, "http_error")


def _normalize_default_message(status_code: int, message: str) -> str:
    """Traduce mensajes genéricos por defecto a un formato más claro y uniforme."""
    default_messages = {
        (status.HTTP_401_UNAUTHORIZED,       "Not authenticated"): "No autenticado. Debes iniciar sesión para acceder a este recurso.",
        (status.HTTP_403_FORBIDDEN,          "Forbidden"):         "No tienes permisos para acceder a este recurso.",
        (status.HTTP_404_NOT_FOUND,          "Not Found"):         "Recurso no encontrado.",
        (status.HTTP_405_METHOD_NOT_ALLOWED, "Method Not Allowed"):"Método HTTP no permitido para este endpoint.",
    }
    return default_messages.get((status_code, message), message)


def _build_error_payload(
    request: Request,
    status_code: int,
    message: str,
    *,
    code: str | None = None,
    details: Any = None,
) -> dict[str, Any]:
    """Construye el payload estándar de error que se devuelve al cliente."""
    return {
        "success": False,
        "error": {
            "code":      code or _status_to_code(status_code),
            "message":   message,
            "details":   details,
            "path":      request.url.path,
            "method":    request.method,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


def _clean_validation_error(e: dict) -> dict:
    """Elimina o decodifica campos bytes que rompen la serialización JSON."""
    cleaned = dict(e)
    inp = cleaned.get("input")
    if isinstance(inp, bytes):
        cleaned["input"] = inp.decode("utf-8", errors="replace")
    # ctx puede contener objetos no serializables también
    if "ctx" in cleaned:
        cleaned["ctx"] = {
            k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
            for k, v in cleaned["ctx"].items()
        }
    return cleaned


async def http_exception_handler(
    request: Request,
    exc: HTTPException | StarletteHTTPException,
) -> JSONResponse:
    """Normaliza cualquier HTTPException lanzada por FastAPI o Starlette."""
    detail = exc.detail

    if isinstance(detail, dict):
        message       = detail.get("message") or detail.get("detail") or "Ocurrió un error en la solicitud."
        code          = detail.get("code")
        extra_details = detail.get("details")
    elif isinstance(detail, list):
        message       = "La solicitud contiene errores de validación."
        code          = "validation_error"
        extra_details = detail
    else:
        message       = _normalize_default_message(exc.status_code, str(detail))
        code          = None
        extra_details = None

    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_payload(
            request,
            exc.status_code,
            message,
            code=code,
            details=extra_details,
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Estandariza los errores automáticos de validación de FastAPI/Pydantic."""
    errors_limpios = [_clean_validation_error(e) for e in exc.errors()]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,  # ✅ corregido
        content=_build_error_payload(
            request,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "La solicitud contiene errores de validación.",
            code="validation_error",
            details=errors_limpios,
        ),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Captura errores no controlados y evita filtrar trazas internas al cliente."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_payload(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Ocurrió un error interno en el servidor.",
            code="internal_server_error",
            details=None,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos los manejadores globales de error en la app FastAPI."""
    app.add_exception_handler(HTTPException,          http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception,              unhandled_exception_handler)