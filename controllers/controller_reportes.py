# controllers/controller_reportes.py

"""Controladores del módulo de reportes.

Se usan para registrar incidencias o bitácoras de actividad y para consultarlas
aplicando filtros simples desde query params.
"""

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep, DriverDep
from core.response_builders import success_response
from schemas.schema_reportes import ReporteCreate, ReporteResponse, ReporteDriverCreate, ReporteDriverResponse, ReporteTerminadoUpdate
from services.service_reportes import ReporteService
from models.model_usuarios import Usuario


async def crear_reporte(
    data: ReporteCreate = Depends(ReporteCreate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> ReporteResponse:
    """Registra un nuevo reporte de actividad en la bitácora del sistema."""
    reporte = await ReporteService(db).registrar_reporte(data)
    return success_response(data=reporte, message="Reporte registrado exitosamente.")


async def listar_reportes(
    id_usuario: int | None = Query(default=None),
    asunto:     str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[ReporteResponse]:
    """Lista reportes, opcionalmente filtrados por usuario o asunto."""
    reportes = await ReporteService(db).obtener_reportes(id_usuario=id_usuario, asunto=asunto)
    return success_response(data=reportes, message="Reportes obtenidos exitosamente.")


async def obtener_reporte(
    id_reporte: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> ReporteResponse:
    """Obtiene un reporte específico por su ID."""
    reporte = await ReporteService(db).obtener_reporte_por_id(id_reporte)
    return success_response(data=reporte, message="Reporte obtenido exitosamente.")


async def terminar_reporte(
    id_reporte: int,
    data: ReporteTerminadoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> ReporteResponse:
    """Marca un reporte como terminado con notas de finalización."""
    reporte = await ReporteService(db).terminar_reporte(id_reporte, data.notas_terminacion)
    return success_response(data=reporte, message="Reporte marcado como terminado exitosamente.")

# Driver methods
async def crear_reporte_driver(
    data: ReporteDriverCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = DriverDep,
) -> ReporteDriverResponse:
    """Crea un nuevo reporte como conductor con fotos y prioridad."""
    reporte = await ReporteService(db).crear_reporte_conductor(data, current_user.id_usuario)
    response = ReporteDriverResponse.from_reporte_actividad(reporte)
    return success_response(data=response, message="Reporte creado exitosamente.")


async def listar_reportes_driver(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = DriverDep,
) -> list[ReporteDriverResponse]:
    """Lista los reportes del conductor actual."""
    reportes = await ReporteService(db).obtener_reportes_conductor(current_user.id_usuario)
    responses = [ReporteDriverResponse.from_reporte_actividad(reporte) for reporte in reportes]
    return success_response(data=responses, message="Reportes del conductor obtenidos exitosamente.")


async def obtener_reporte_driver(
    id_reporte: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = DriverDep,
) -> ReporteDriverResponse:
    """Obtiene un reporte específico del conductor."""
    reporte = await ReporteService(db).obtener_reporte_conductor_por_id(id_reporte, current_user.id_usuario)
    response = ReporteDriverResponse.from_reporte_actividad(reporte)
    return success_response(data=response, message="Reporte obtenido exitosamente.")