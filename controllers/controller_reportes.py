# controllers/controller_reportes.py

"""Controladores del módulo de reportes.

Se usan para registrar incidencias o bitácoras de actividad y para consultarlas
aplicando filtros simples desde query params.
"""

from fastapi import Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep, DriverDep
from core.response_builders import success_response, error_response
from schemas.schema_reportes import ReporteCreate, ReporteResponse, ReporteDriverCreate, ReporteDriverResponse, ReporteTerminadoUpdate
from services.service_reportes import ReporteService
from models.model_usuarios import Usuario
import logging

logger = logging.getLogger(__name__)

async def crear_reporte(
    data: ReporteCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> ReporteResponse:
    """Registra un nuevo reporte de actividad en la bitácora del sistema."""
    try:
        reporte = await ReporteService(db).registrar_reporte(data)
        return success_response(data=reporte, message="Reporte registrado exitosamente.")
    except Exception as e:
        logger.error(f"Error al crear reporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al registrar el reporte: {str(e)}"
        )


async def listar_reportes(
    id_usuario: int | None = Query(default=None),
    asunto:     str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[ReporteResponse]:
    """Lista reportes, opcionalmente filtrados por usuario o asunto."""
    try:
        reportes = await ReporteService(db).obtener_reportes(id_usuario=id_usuario, asunto=asunto)
        return success_response(data=reportes, message="Reportes obtenidos exitosamente.")
    except Exception as e:
        logger.error(f"Error al listar reportes: {str(e)}", exc_info=True)
        # Fallback: retornar lista vacía en lugar de error 500
        return success_response(data=[], message="No hay reportes disponibles o error temporal al cargar reportes.")


async def obtener_reporte(
    id_reporte: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> ReporteResponse:
    """Obtiene un reporte específico por su ID."""
    try:
        reporte = await ReporteService(db).obtener_reporte_por_id(id_reporte)
        if not reporte:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado.")
        return success_response(data=reporte, message="Reporte obtenido exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener reporte {id_reporte}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el reporte solicitado."
        )


async def terminar_reporte(
    id_reporte: int,
    data: ReporteTerminadoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> ReporteResponse:
    """Marca un reporte como terminado con notas de finalización."""
    try:
        reporte = await ReporteService(db).terminar_reporte(id_reporte, data.notas_terminacion)
        if not reporte:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado.")
        return success_response(data=reporte, message="Reporte marcado como terminado exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al terminar reporte {id_reporte}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al finalizar el reporte."
        )

# Driver methods
async def crear_reporte_driver(
    data: ReporteDriverCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = DriverDep,
) -> ReporteDriverResponse:
    """Crea un nuevo reporte como conductor con fotos y prioridad."""
    try:
        reporte = await ReporteService(db).crear_reporte_conductor(data, current_user.id_usuario, current_user.correo)
        response = ReporteDriverResponse.from_reporte_actividad(reporte)
        return success_response(data=response, message="Reporte creado exitosamente.")
    except Exception as e:
        logger.error(f"Error al crear reporte driver: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el reporte del conductor: {str(e)}"
        )


async def listar_reportes_driver(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = DriverDep,
) -> list[ReporteDriverResponse]:
    """Lista los reportes del conductor actual."""
    try:
        reportes = await ReporteService(db).obtener_reportes_conductor(current_user.id_usuario)
        responses = [ReporteDriverResponse.from_reporte_actividad(reporte) for reporte in reportes]
        return success_response(data=responses, message="Reportes del conductor obtenidos exitosamente.")
    except Exception as e:
        logger.error(f"Error al listar reportes driver: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los reportes del conductor."
        )


async def obtener_reporte_driver(
    id_reporte: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = DriverDep,
) -> ReporteDriverResponse:
    """Obtiene un reporte específico del conductor."""
    try:
        reporte = await ReporteService(db).obtener_reporte_conductor_por_id(id_reporte, current_user.id_usuario)
        if not reporte:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado para este conductor.")
        response = ReporteDriverResponse.from_reporte_actividad(reporte)
        return success_response(data=response, message="Reporte obtenido exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener reporte driver {id_reporte}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el reporte del conductor."
        )
