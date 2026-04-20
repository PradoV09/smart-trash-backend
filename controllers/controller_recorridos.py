"""Controladores para recorridos en API externa."""

from __future__ import annotations

from uuid import UUID

from core.response_builders import success_response
from schemas.schema_recorridos_externos import (
    IniciarRecorridoRequest,
    RecorridoResponse,
    RegistrarPosicionRequest,
)
from schemas.schema_responses import SuccessResponse
from services.service_api_externa import APIExternaService


async def iniciar_recorrido(
    data: IniciarRecorridoRequest,
) -> SuccessResponse[RecorridoResponse]:
    recorrido = await APIExternaService().iniciar_recorrido(data)
    return success_response(
        data=recorrido,
        message="Recorrido iniciado exitosamente en la API externa.",
    )


async def registrar_posicion(
    recorrido_id: UUID,
    data: RegistrarPosicionRequest,
) -> SuccessResponse[RecorridoResponse]:
    posicion = await APIExternaService().registrar_posicion(str(recorrido_id), data)
    return success_response(
        data=posicion,
        message="Posición registrada exitosamente en la API externa.",
    )
