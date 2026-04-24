"""Controladores para gestión de posiciones GPS del recorrido."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, DriverDep, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_posiciones import PosicionCreate, PosicionResponse, PosicionListResponse
from models.model_usuarios import Usuario
from services.service_posiciones import PosicionesService
from models.model_asignacionrutas import EstadoAsignacion
import logging

logger = logging.getLogger(__name__)


async def registrar_posicion(
    id_asignacion: int,
    data: PosicionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> SuccessResponse[PosicionResponse]:
    """Registra una nueva posición GPS para una asignación.
    
    El driver solo puede registrar posiciones en asignaciones que:
    - Le pertenezcan (misma asignación que tiene asignada)
    - Estén en estado 'en_curso'
    """
    service = PosicionesService(db)
    
    # Validar que la asignación existe y está en curso
    posicion = await service.registrar_posicion(id_asignacion, data)
    
    return success_response(
        data=posicion,
        message="Posición registrada exitosamente."
    )


async def listar_posiciones_admin(
    id_asignacion: int,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[PosicionListResponse]:
    """Lista todas las posiciones de una asignación con paginación."""
    service = PosicionesService(db)
    
    result = await service.listar_posiciones(id_asignacion, page, page_size)
    
    return success_response(
        data=result,
        message="Posiciones obtenidas exitosamente."
    )


async def obtener_ultima_posicion(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[PosicionResponse | None]:
    """Obtiene la última posición registrada de una asignación."""
    service = PosicionesService(db)
    
    posicion = await service.obtener_ultima_posicion(id_asignacion)
    
    return success_response(
        data=posicion,
        message="Última posición obtenida exitosamente."
    )