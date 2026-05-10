"""Controladores para recorridos en API externa."""

from __future__ import annotations
from uuid import UUID
from fastapi import HTTPException, status
from core.dependecies import DriverDep
from core.response_builders import success_response
from models.model_usuarios import Usuario
from schemas.schema_recorridos_externos import (
    IniciarRecorridoRequest,
    PosicionesRecorridoResponse,
    RecorridoResponse,
    RegistrarPosicionRequest,
)
from schemas.schema_responses import SuccessResponse
from services.service_api_externa import APIExternaService
import logging

logger = logging.getLogger(__name__)

async def iniciar_recorrido(
    data: IniciarRecorridoRequest,
) -> SuccessResponse[RecorridoResponse]:
    """Inicia un recorrido en la API externa."""
    try:
        recorrido = await APIExternaService().iniciar_recorrido(data)
        return success_response(
            data=recorrido,
            message="Recorrido iniciado exitosamente en la API externa.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al iniciar recorrido externo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar con el servicio externo de recorridos: {str(e)}"
        )


async def registrar_posicion(
    recorrido_id: UUID,
    data: RegistrarPosicionRequest,
    _: Usuario = DriverDep,
) -> SuccessResponse[RecorridoResponse]:
    """Registra una posición GPS en un recorrido de la API externa."""
    try:
        posicion = await APIExternaService().registrar_posicion(str(recorrido_id), data)
        return success_response(
            data=posicion,
            message="Posición registrada exitosamente en la API externa.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar posición externa en recorrido {recorrido_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar posición al servicio externo: {str(e)}"
        )


async def listar_posiciones(
    recorrido_id: UUID,
    perfil_id: str | None,
) -> SuccessResponse[list[PosicionesRecorridoResponse] | PosicionesRecorridoResponse]:
    """Lista posiciones GPS de un recorrido desde la API externa."""
    try:
        posiciones = await APIExternaService().listar_posiciones_recorrido(str(recorrido_id), perfil_id)
        return success_response(
            data=posiciones,
            message="Posiciones obtenidas exitosamente desde la API externa.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al listar posiciones externas de recorrido {recorrido_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar posiciones del servicio externo: {str(e)}"
        )
