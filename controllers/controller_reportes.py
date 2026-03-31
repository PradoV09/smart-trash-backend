# controllers/reporte_controller.py

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from schemas.schema_reportes import ReporteCreate, ReporteResponse
from services.service_reportes import ReporteService
from models.model_usuarios import Usuario

async def crear_reporte(
    data: ReporteCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> ReporteResponse:
    return await ReporteService(db).registrar_reporte(data)

async def listar_reportes(
    id_usuario: int | None = Query(default=None),
    asunto:     str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[ReporteResponse]:
    return await ReporteService(db).obtener_reportes(id_usuario=id_usuario, asunto=asunto)