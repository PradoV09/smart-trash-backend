"""Controladores para gestión de posiciones GPS del recorrido."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, DriverDep, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_posiciones import (
    PosicionCreate,
    PosicionResponse,
    PosicionListResponse,
    PosicionImagenCreate,
    PosicionImagenResponse,
)
from models.model_usuarios import Usuario
from services.service_posiciones import PosicionesService
import logging

logger = logging.getLogger(__name__)


async def registrar_posicion(
    id_asignacion: int,
    data: PosicionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> SuccessResponse[PosicionResponse]:
    """Registra una nueva posición GPS para una asignación."""
    try:
        logger.info(f"Recibiendo posición para asignación {id_asignacion}: {data.model_dump()}")
        service = PosicionesService(db)
        posicion = await service.registrar_posicion(id_asignacion, data)
        return success_response(
            data=posicion,
            message="Posición registrada exitosamente."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar posición en asignación {id_asignacion}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al registrar la posición GPS: {str(e)}"
        )


async def listar_posiciones_admin(
    id_asignacion: int,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[PosicionListResponse]:
    """Lista todas las posiciones de una asignación con paginación."""
    try:
        service = PosicionesService(db)
        result = await service.listar_posiciones(id_asignacion, page, page_size)
        return success_response(
            data=result,
            message="Posiciones obtenidas exitosamente."
        )
    except Exception as e:
        logger.error(f"Error al listar posiciones de asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el historial de posiciones."
        )


async def obtener_ultima_posicion(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[PosicionResponse | None]:
    """Obtiene la última posición registrada de una asignación."""
    try:
        service = PosicionesService(db)
        posicion = await service.obtener_ultima_posicion(id_asignacion)
        return success_response(
            data=posicion,
            message="Última posición obtenida exitosamente."
        )
    except Exception as e:
        logger.error(f"Error al obtener última posición de asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar la última posición GPS."
        )


async def registrar_imagen_posicion(
    posicion_id: str,
    data: PosicionImagenCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> SuccessResponse[PosicionImagenResponse]:
    """Registra o actualiza la imagen asociada a una posición específica."""
    try:
        service = PosicionesService(db)
        imagen = await service.registrar_imagen_posicion(posicion_id, data.imagen_base64)
        return success_response(
            data=imagen,
            message="Imagen registrada correctamente."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar imagen para posición {posicion_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la imagen."
        )


async def obtener_posiciones_activas(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse:
    """Obtiene las posiciones más recientes de todos los vehículos activos en ruta."""
    try:
        service = PosicionesService(db)
        posiciones = await service.obtener_posiciones_activas()
        return success_response(
            data=posiciones,
            message="Posiciones activas obtenidas exitosamente."
        )
    except Exception as e:
        logger.error(f"Error al obtener posiciones activas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar posiciones activas."
        )