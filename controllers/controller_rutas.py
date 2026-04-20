"""Controladores para creación de rutas en API externa."""

from __future__ import annotations

from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_rutas_externas import RutasCreateRequest, RutasCreateResponse
from services.service_api_externa import APIExternaService


async def crear_ruta(data: RutasCreateRequest) -> SuccessResponse[RutasCreateResponse]:
    ruta = await APIExternaService().crear_ruta(data)
    return success_response(
        data=ruta,
        message="Ruta creada exitosamente en la API externa.",
    )
