"""Controladores para estado en vivo de asignaciones (admin)."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_estado_vivo import EstadoVivoResponse
from models.model_usuarios import Usuario
from services.service_estado_vivo import EstadoVivoService
import logging

logger = logging.getLogger(__name__)


async def obtener_estado_vivo(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[EstadoVivoResponse]:
    """Obtiene el estado en vivo de una asignación."""
    try:
        service = EstadoVivoService(db)
        estado = await service.obtener_estado_vivo(id_asignacion)
        
        return success_response(
            data=estado,
            message="Estado vivo obtenido exitosamente."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener estado vivo de asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al recuperar el estado en vivo."
        )