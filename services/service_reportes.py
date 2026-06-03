# services/service_reportes.py

"""Servicios del módulo de reportes.

Permiten registrar actividad o incidencias y consultarlas aplicando filtros
básicos para auditoría operativa.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.model_reportes import ReporteActividad
from schemas.schema_reportes import ReporteCreate
import logging

logger = logging.getLogger(__name__)


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

    async def crear_reporte_conductor(self, data, id_usuario: int, u_gmail_cache: str | None = None) -> ReporteActividad:
        """Crea un reporte como conductor con fotos y prioridad."""
        from datetime import datetime

        # Guardar el estado en la descripción o en u_rol_cache como workaround
        # ya que el modelo no tiene campo 'estado'
        descripcion_con_estado = f"[PRIORIDAD: {data.estado.upper()}] {data.descripcion}"

        # Crear reporte con los campos disponibles del modelo
        # Usar datetime sin timezone para compatibilidad con la BD
        reporte = ReporteActividad(
            id_usuario=id_usuario,
            u_gmail_cache=u_gmail_cache,
            asunto=data.asunto,
            descripcion=descripcion_con_estado,
            u_rol_cache=data.estado,  # Guardamos el estado aquí como workaround
            fecha=datetime.now(),  # Sin timezone para compatibilidad
            latitud=getattr(data, 'latitud', None),
            longitud=getattr(data, 'longitud', None)
        )

        self.db.add(reporte)
        await self.db.flush()

        # Procesar fotos si existen
        if hasattr(data, 'fotos') and data.fotos:
            await self._procesar_fotos(reporte, data.fotos, getattr(data, 'id_asignacion', None))

        return reporte

    async def _procesar_fotos(self, reporte: ReporteActividad, fotos_data: list[dict], id_asignacion: int | None = None):
        """Procesa las fotos enviadas en un reporte de conductor."""
        from services.service_fotos import FotosService
        from schemas.schema_fotos import FotoCreate
        from services.service_api_externa import APIExternaService
        from models.model_asignacion_externa import AsignacionExterna
        from sqlalchemy import select
        from datetime import datetime
        from core.config import get_external_api_config

        fotos_service = FotosService(self.db)
        urls = []

        # Obtener recorrido_externo_id y perfil_id si existe asignación
        recorrido_externo_id = None
        perfil_id = None
        if id_asignacion:
            try:
                result = await self.db.execute(
                    select(AsignacionExterna).where(AsignacionExterna.id_asignacion == id_asignacion)
                )
                asignacion_externa = result.scalar_one_or_none()
                if asignacion_externa:
                    if asignacion_externa.recorrido_externo_id:
                        recorrido_externo_id = asignacion_externa.recorrido_externo_id
                    # Obtener perfil_id de configuración
                    cfg = get_external_api_config()
                    perfil_id = cfg.perfil_id
            except Exception as e:
                logger.warning(f"No se pudo obtener recorrido_externo_id para asignación {id_asignacion}: {str(e)}")

        for foto_dict in fotos_data:
            try:
                # Normalizar nombres de campos comunes para FotoCreate
                if 'base64' in foto_dict and 'imagen_base64' not in foto_dict:
                    foto_dict['imagen_base64'] = foto_dict['base64']

                # Si hay id_asignacion, intentamos el flujo formal de registro de fotos
                if id_asignacion:
                    try:
                        # Aseguramos que el dict tenga los campos necesarios para FotoCreate
                        if 'timestamp' not in foto_dict or not foto_dict['timestamp']:
                            foto_dict['timestamp'] = datetime.now()
                        if 'tipo' not in foto_dict or not foto_dict['tipo']:
                            foto_dict['tipo'] = 'incidencia'

                        # Si sigue faltando imagen_base64, saltamos esta foto o registramos el error
                        if 'imagen_base64' not in foto_dict:
                            logger.error(f"Foto omitida: falta el contenido base64. Campos presentes: {list(foto_dict.keys())}")
                            continue

                        foto_create = FotoCreate(**foto_dict)
                        res = await fotos_service.registrar_foto(id_asignacion, foto_create)
                        urls.append(res.url)
                    except Exception as e:
                        logger.warning(f"No se pudo registrar foto formalmente para asignación {id_asignacion}: {str(e)}. Reintentando flujo simple.")
                        # Si falla (ej. asignación no en curso), intentamos flujo simple
                        id_asignacion = None

                if not id_asignacion:
                    # Flujo simplificado: solo guardar el archivo
                    if 'imagen_base64' in foto_dict:
                        datos_imagen, extension = fotos_service._validar_imagen_base64(foto_dict['imagen_base64'])
                        url = await fotos_service._guardar_imagen(datos_imagen, extension, reporte.id_usuario or 0)
                        urls.append(url)

                # Enviar imagen a API externa si hay recorrido_externo_id y lat/lon
                if recorrido_externo_id and 'imagen_base64' in foto_dict and reporte.latitud and reporte.longitud and perfil_id:
                    try:
                        api_service = APIExternaService()
                        # Primero registrar la posición en la API externa
                        posicion_response = await api_service.registrar_posicion_externa(
                            recorrido_externo_id=recorrido_externo_id,
                            latitud=reporte.latitud,
                            longitud=reporte.longitud,
                            perfil_id=perfil_id
                        )
                        logger.info(f"Posición registrada en API externa para reporte {reporte.id_registro}: {posicion_response}")

                        # Si la respuesta incluye un posicion_id, intentar subir la imagen
                        if posicion_response and 'id' in posicion_response:
                            posicion_id = posicion_response['id']
                            # Nota: La API externa debe tener el endpoint POST /api/recorridos/posiciones/{posicion_id}/imagen
                            # Por ahora, logueamos la intención ya que este endpoint puede no estar implementado
                            logger.info(f"Imagen podría subirse a posición {posicion_id} en API externa")
                    except Exception as e:
                        logger.warning(f"No se pudo enviar posición/imagen a API externa: {str(e)}")
            except Exception as e:
                logger.error(f"Error crítico procesando foto en reporte: {str(e)}")
                continue

        if urls:
            # Guardamos la primera URL en el reporte como evidencia principal
            reporte.evidencia_url = urls[0]
            await self.db.flush()

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
