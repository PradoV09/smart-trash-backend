# controllers/controller_asignaciovehiculo.py

"""Controladores del módulo de asignaciones y tripulación.

Este archivo organiza los endpoints por perfil de acceso:
- admin,
- driver,
- recolector,
- ciudadano.

Los controllers solo coordinan dependencias, permisos y respuestas.
La lógica de operación de rutas vive en los services.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep, DriverDep, RecolectorDep, UserDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_asignacionrutas import (
    AsignacionCreate,
    AsignacionResponse,
    AsignacionPublicResponse,
)
from services.service_asignacionrutas import AsignacionService
from models.model_usuarios import Usuario
import logging

logger = logging.getLogger(__name__)

# --- Admin ---
async def crear_asignacion(
    data: AsignacionCreate = Depends(AsignacionCreate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Crea una nueva asignación de vehículo para una ruta externa."""
    try:
        asignacion = await AsignacionService(db).crear_asignacion(data)
        return success_response(data=asignacion, message="Asignación creada exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear asignación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la asignación: {str(e)}"
        )


async def listar_asignaciones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[AsignacionResponse]]:
    """Lista todas las asignaciones con vehículo y tripulación asociada."""
    try:
        asignaciones = await AsignacionService(db).obtener_asignaciones()
        return success_response(data=asignaciones, message="Asignaciones obtenidas exitosamente.")
    except Exception as e:
        logger.error(f"Error al listar asignaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la lista de asignaciones."
        )


async def obtener_detalles_ruta(
    id_ruta: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[dict]:
    """Obtiene los detalles completos de una ruta desde el servicio externo de rutas."""
    try:
        detalles = await AsignacionService(db).obtener_detalles_ruta(id_ruta)
        if not detalles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron detalles para la ruta con id {id_ruta}.",
            )
        return success_response(data=detalles, message="Detalles de ruta obtenidos exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener detalles de ruta {id_ruta}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar detalles de la ruta externa."
        )


async def obtener_asignacion_admin(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Obtiene el detalle de una asignación desde el contexto administrativo."""
    try:
        asignacion = await AsignacionService(db).obtener_asignacion_id(id_asignacion)
        if not asignacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignación no encontrada.")
        return success_response(data=asignacion, message="Asignación obtenida exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar la asignación."
        )


async def cancelar_asignacion(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Cancela una asignación y libera el vehículo asociado."""
    try:
        asignacion = await AsignacionService(db).cancelar_asignacion(id_asignacion)
        return success_response(data=asignacion, message="Asignación cancelada exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cancelar asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cancelar la asignación."
        )


# --- Driver ---
async def ver_asignacion_driver(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = DriverDep,
) -> AsignacionResponse:
    """Permite al conductor consultar la asignación que debe operar.
    
    El driver solo puede ver SU asignación (la que tiene asignada).
    """
    try:
        # TODO: Implementar validación de que el driver tiene esta asignación
        # Por ahora permitimos cualquier asignación para el driver
        asignacion = await AsignacionService(db).obtener_asignacion_id(id_asignacion)
        if not asignacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignación no encontrada.")
        return success_response(data=asignacion, message="Asignación del conductor obtenida exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al ver asignación driver {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la asignación del conductor."
        )


async def iniciar_recorrido(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    """Inicia el recorrido integrando con la API externa."""
    try:
        asignacion = await AsignacionService(db).iniciar_recorrido_con_api_externa(id_asignacion)
        return success_response(data=asignacion, message="Recorrido iniciado exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al iniciar recorrido {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar el recorrido: {str(e)}"
        )


async def finalizar_recorrido(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    """Finaliza el recorrido integrando con la API externa."""
    try:
        asignacion = await AsignacionService(db).finalizar_recorrido_con_api_externa(id_asignacion)
        return success_response(data=asignacion, message="Recorrido finalizado exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al finalizar recorrido {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al finalizar el recorrido: {str(e)}"
        )


# --- Recolector ---
async def ver_asignacion_recolector(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> AsignacionResponse:
    """Permite al recolector consultar los datos de su asignación."""
    try:
        asignacion = await AsignacionService(db).obtener_asignacion_id(id_asignacion)
        if not asignacion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignación no encontrada.")
        return success_response(data=asignacion, message="Asignación del recolector obtenida exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al ver asignación recolector {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la asignación del recolector."
        )


# --- User ciudadano ---
async def ver_horario_ruta(
    id_ruta: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = UserDep,
) -> AsignacionPublicResponse:
    """Consulta el horario disponible para una ruta externa específica."""
    try:
        asignacion = await AsignacionService(db).obtener_asignacion_ruta(id_ruta)
        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró información de horario para la ruta externa '{id_ruta}'.",
            )
        return success_response(data=asignacion, message="Horario de ruta obtenido exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al ver horario ruta {id_ruta}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el horario de la ruta."
        )


async def verificar_asignacion_usuario(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = UserDep,
) -> AsignacionPublicResponse:
    """Expone una consulta puntual de asignación desde el contexto del usuario final."""
    try:
        asignacion = await AsignacionService(db).obtener_asignacion_id(id_asignacion)
        return success_response(data=asignacion, message="Asignación del usuario obtenida exitosamente.")
    except Exception as e:
        logger.error(f"Error al verificar asignación usuario {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar la asignación."
        )


async def verificar_asignacion_pendiente(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Valida que una asignación siga pendiente antes de cambiar su tripulación."""
    try:
        asignacion = await AsignacionService(db).verificar_asignacion_pendiente(id_asignacion)
        return success_response(data=asignacion, message="Asignación pendiente validada exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al verificar asignación pendiente {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al validar el estado de la asignación."
        )


async def validar_tripulacion_con_piloto(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[dict]:
    """Valida que la tripulación tenga al menos un conductor (piloto)."""
    try:
        await AsignacionService(db).validar_tripulacion_con_piloto(id_asignacion)
        return success_response(
            data={"valid": True, "message": "La tripulación tiene conductor asignado"},
            message="Validación de tripulación con piloto exitosa."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al validar piloto en asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al validar la tripulación."
        )
