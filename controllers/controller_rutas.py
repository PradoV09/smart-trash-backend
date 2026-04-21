"""Controladores para creación de rutas en API externa."""

from __future__ import annotations

from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_rutas_externas import RutasCreateRequest, RutasCreateResponse
from services.service_api_externa import APIExternaService


from fastapi import HTTPException, status
from schemas.schema_rutas_externas import RutasCreateRequest, RutasCreateResponse, RutaResponse

async def crear_ruta(data: RutasCreateRequest) -> SuccessResponse[RutasCreateResponse]:
    ruta = await APIExternaService().crear_ruta(data)
    return success_response(
        data=ruta,
        message="Ruta creada exitosamente en la API externa.",
    )


async def listar_rutas(perfil_id: str | None) -> SuccessResponse[list[RutaResponse]]:
    resp = await APIExternaService().listar_rutas(perfil_id)
    # The external API returns {"data": [...]}. Extract it.
    rutas = resp.get("data", []) if isinstance(resp, dict) else resp
    return success_response(
        data=rutas,
        message="Rutas obtenidas exitosamente desde la API externa.",
    )


async def obtener_ruta(id: str, perfil_id: str | None) -> SuccessResponse[RutaResponse]:
    resp = await APIExternaService().obtener_ruta(id, perfil_id)
    ruta = resp.get("data", resp) if isinstance(resp, dict) else resp
    return success_response(
        data=ruta,
        message="Ruta obtenida exitosamente desde la API externa.",
    )
