# services/service_reportes.py

"""Servicios del módulo de reportes.

Permiten registrar actividad o incidencias y consultarlas aplicando filtros
básicos para auditoría operativa.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.model_reportes import ReporteActividad
from schemas.schema_reportes import ReporteCreate


class ReporteService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def registrar_reporte(self, data: ReporteCreate) -> ReporteActividad:
        """Crea un nuevo registro de actividad en la tabla de reportes."""
        reporte = ReporteActividad(**data.model_dump())
        self.db.add(reporte)
        await self.db.flush()
        return reporte

    async def obtener_reportes(
        self,
        id_usuario: int | None = None,
        asunto:     str | None = None,
    ) -> list[ReporteActividad]:
        """Recupera reportes ordenados por fecha descendente y permite filtrado simple."""
        query = select(ReporteActividad)
        if id_usuario:
            query = query.where(ReporteActividad.id_usuario == id_usuario)
        if asunto:
            query = query.where(ReporteActividad.asunto == asunto)
        result = await self.db.execute(
            query.order_by(ReporteActividad.fecha.desc())
        )
        return result.scalars().all()
