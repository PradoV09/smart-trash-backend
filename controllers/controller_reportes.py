# controllers/controller_reportes.py

"""Controladores del módulo de reportes.

Se usan para registrar incidencias o bitácoras de actividad y para consultarlas
aplicando filtros simples desde query params.
"""

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from schemas.schema_reportes import ReporteCreate, ReporteResponse
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