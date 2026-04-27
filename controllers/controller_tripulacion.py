# controllers/controller_tripulacion.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from schemas.schema_tripulacion import TripulacionCreate, TripulacionResponse
from services.service_tripulacion import TripulacionService
from models.model_usuarios import Usuario
import logging

logger = logging.getLogger(__name__)

async def crear_tripulacion(
    data: TripulacionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> TripulacionResponse:
    """Crea una nueva tripulación para una asignación."""
    try:
        tripulacion = await TripulacionService(db).crear_tripulacion(data)
        return success_response(data=tripulacion, message="Tripulación creada exitosamente.")
    except Exception as e:
        logger.error(f"Error al crear tripulación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la tripulación: {str(e)}"
        )

async def listar_tripulaciones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[TripulacionResponse]:
    """Lista todas las tripulaciones registradas."""
    try:
        tripulaciones = await TripulacionService(db).obtener_todas()
        return success_response(data=tripulaciones, message="Tripulaciones obtenidas exitosamente.")
    except Exception as e:
        logger.error(f"Error al listar tripulaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el listado de tripulaciones."
        )
