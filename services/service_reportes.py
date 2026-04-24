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

    async def obtener_reporte_por_id(self, id_reporte: int) -> ReporteActividad:
        """Obtiene un reporte específico por su ID."""
        query = select(ReporteActividad).where(ReporteActividad.id_registro == id_reporte)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def terminar_reporte(self, id_reporte: int, notas_terminacion: str) -> ReporteActividad:
        """Marca un reporte como terminado."""
        from datetime import datetime
        
        query = select(ReporteActividad).where(ReporteActividad.id_registro == id_reporte)
        result = await self.db.execute(query)
        reporte = result.scalar_one_or_none()
        
        if reporte:
            # Como workaround, agregamos las notas de terminación a la descripción
            # ya que el modelo no tiene campos 'terminado', 'notas_terminacion', 'fecha_terminacion'
            reporte.descripcion = f"{reporte.descripcion}\n\n[TERMINADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {notas_terminacion}"
            await self.db.flush()
        
        return reporte

    async def crear_reporte_conductor(self, data, id_usuario: int) -> ReporteActividad:
        """Crea un reporte como conductor con fotos y prioridad."""
        from datetime import datetime
        
        # Guardar el estado en la descripción o en u_rol_cache como workaround
        # ya que el modelo no tiene campo 'estado'
        descripcion_con_estado = f"[PRIORIDAD: {data.estado.upper()}] {data.descripcion}"
        
        # Crear reporte con los campos disponibles del modelo
        # Usar datetime sin timezone para compatibilidad con la BD
        reporte = ReporteActividad(
            id_usuario=id_usuario,
            asunto=data.asunto,
            descripcion=descripcion_con_estado,
            u_rol_cache=data.estado,  # Guardamos el estado aquí como workaround
            fecha=datetime.now()  # Sin timezone para compatibilidad
        )
        
        self.db.add(reporte)
        await self.db.flush()
        
        # TODO: Procesar fotos si existen
        # if data.fotos:
        #     await self._procesar_fotos(reporte.id_registro, data.fotos)
        
        return reporte

    async def obtener_reportes_conductor(self, id_usuario: int) -> list[ReporteActividad]:
        """Obtiene los reportes de un conductor específico."""
        query = select(ReporteActividad).where(ReporteActividad.id_usuario == id_usuario)
        result = await self.db.execute(query.order_by(ReporteActividad.fecha.desc()))
        return result.scalars().all()

    async def obtener_reporte_conductor_por_id(self, id_reporte: int, id_usuario: int) -> ReporteActividad:
        """Obtiene un reporte específico de un conductor."""
        query = select(ReporteActividad).where(
            ReporteActividad.id_registro == id_reporte,
            ReporteActividad.id_usuario == id_usuario
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
