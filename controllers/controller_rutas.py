"""Controladores para creación de rutas en API externa."""

from __future__ import annotations
from fastapi import HTTPException, status
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_rutas_externas import RutasCreateRequest, RutasCreateResponse, RutaResponse
from services.service_api_externa import APIExternaService
import logging

logger = logging.getLogger(__name__)

async def crear_ruta(data: RutasCreateRequest) -> SuccessResponse[RutasCreateResponse]:
    """Crea una nueva ruta en la API externa."""
    try:
        ruta = await APIExternaService().crear_ruta(data)
        return success_response(
            data=ruta,
            message="Ruta creada exitosamente en la API externa.",
        )
    except Exception as e:
        logger.error(f"Error al crear ruta externa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar con el servicio externo de rutas: {str(e)}"
        )


async def listar_rutas(perfil_id: str | None) -> SuccessResponse[list[RutaResponse]]:
    """Lista rutas disponibles en la API externa."""
    try:
        resp = await APIExternaService().listar_rutas(perfil_id)
        # The external API returns {"data": [...]}. Extract it.
        rutas = resp.get("data", []) if isinstance(resp, dict) else resp
        return success_response(
            data=rutas,
            message="Rutas obtenidas exitosamente desde la API externa.",
        )
    except Exception as e:
        logger.error(f"Error al listar rutas externas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el listado de rutas externas."
        )


async def obtener_ruta(id: str, perfil_id: str | None) -> SuccessResponse[RutaResponse]:
    """Obtiene el detalle de una ruta específica desde la API externa."""
    try:
        resp = await APIExternaService().obtener_ruta(id, perfil_id)
        ruta = resp.get("data", resp) if isinstance(resp, dict) else resp
        if not ruta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada en el servicio externo.")
        return success_response(
            data=ruta,
            message="Ruta obtenida exitosamente desde la API externa.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener ruta externa {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar detalles de la ruta externa."
        )
