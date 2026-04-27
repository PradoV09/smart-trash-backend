"""Controladores para gestión de fotos/evidencia del recorrido."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, DriverDep, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_fotos import FotoCreate, FotoResponse, FotoListResponse
from models.model_usuarios import Usuario
from services.service_fotos import FotosService
import logging

logger = logging.getLogger(__name__)


async def registrar_foto(
    id_asignacion: int,
    data: FotoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> SuccessResponse[FotoResponse]:
    """Registra una nueva foto/evidencia para una asignación."""
    try:
        service = FotosService(db)
        foto = await service.registrar_foto(id_asignacion, data)
        return success_response(
            data=foto,
            message="Foto registrada exitosamente."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar foto en asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al registrar la foto: {str(e)}"
        )


async def listar_fotos_admin(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[FotoListResponse]:
    """Lista todas las fotos de una asignación."""
    try:
        service = FotosService(db)
        result = await service.listar_fotos(id_asignacion)
        return success_response(
            data=result,
            message="Fotos obtenidas exitosamente."
        )
    except Exception as e:
        logger.error(f"Error al listar fotos de asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar la lista de fotos."
        )