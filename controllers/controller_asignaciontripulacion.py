"""Controladores para la gestión de tripulación.

Permite la administración global y por asignación de los miembros del equipo.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep, RecolectorDep, DriverDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_asignaciontripulacion import TripulacionCreate, TripulacionResponse
from models.model_usuarios import Usuario
from services.service_asignaciontripulacion import TripulacionService
import logging

logger = logging.getLogger(__name__)

async def agregar_miembro_tripulacion(
    id_asignacion: int,
    data: TripulacionCreate = Depends(TripulacionCreate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[TripulacionResponse]:
    """Agrega un usuario a la tripulación de una asignación pendiente."""
    try:
        miembro = await TripulacionService(db).agregar_miembro(id_asignacion, data)
        return success_response(data=miembro, message="Miembro agregado a la tripulación exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al agregar miembro a tripulación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar el miembro: {str(e)}"
        )

async def eliminar_miembro_tripulacion(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[dict[str, int]]:
    """Elimina un integrante de la tripulación mientras la asignación siga pendiente."""
    try:
        await TripulacionService(db).eliminar_miembro_asignacion(id_asignacion, id_usuario)
        return success_response(
            data={"id_asignacion": id_asignacion, "id_usuario": id_usuario},
            message="Miembro eliminado de la tripulación exitosamente.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar miembro de tripulación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el miembro de la tripulación."
        )

async def listar_tripulacion_asignacion(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[TripulacionResponse]]:
    """Obtiene los integrantes de la tripulación para una asignación específica."""
    try:
        tripulacion = await TripulacionService(db).obtener_tripulacion_asignacion(id_asignacion)
        return success_response(
            data=tripulacion,
            message=f"Tripulación de la asignación {id_asignacion} obtenida exitosamente."
        )
    except Exception as e:
        logger.error(f"Error al listar tripulación de asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la tripulación de la asignación."
        )

async def ver_tripulacion_driver(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> SuccessResponse[list[TripulacionResponse]]:
    """Permite al conductor ver la tripulación asignada a su ruta."""
    try:
        tripulacion = await TripulacionService(db).obtener_tripulacion_asignacion(id_asignacion)
        return success_response(
            data=tripulacion,
            message="Tripulación obtenida exitosamente por el conductor."
        )
    except Exception as e:
        logger.error(f"Error al ver tripulación driver {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar la tripulación asignada."
        )

async def confirmar_participacion_driver(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = DriverDep,
) -> SuccessResponse[TripulacionResponse]:
    """Confirma la participación del conductor y deja trazabilidad en tiempo real."""
    try:
        miembro = await TripulacionService(db).confirmar_asignacion(id_asignacion, usuario.id_usuario)
        return success_response(data=miembro, message="Participación confirmada exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al confirmar participación driver: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al confirmar la participación en la ruta."
        )

async def listar_todas_tripulaciones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[TripulacionResponse]]:
    """Obtiene el listado completo de todos los tripulantes asignados a cualquier ruta."""
    try:
        tripulaciones = await TripulacionService(db).obtener_todas_tripulaciones()
        return success_response(
            data=tripulaciones, 
            message="Listado global de tripulaciones obtenido exitosamente."
        )
    except Exception as e:
        logger.error(f"Error al listar todas las tripulaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el listado global de tripulaciones."
        )