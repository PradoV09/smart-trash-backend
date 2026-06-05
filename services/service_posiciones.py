"""Servicio para gestión de posiciones GPS del recorrido."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional
import base64
import os
import re
from io import BytesIO
from PIL import Image

from models.model_posiciones import RecorridoPosicion
from models.model_asignacionrutas import AsignacionRutas, EstadoAsignacion
from schemas.schema_posiciones import (
    PosicionCreate,
    PosicionResponse,
    PosicionListResponse,
    PosicionImagenResponse,
)
from core.websocket_manager import ws_manager
from core.config import get_app_config
import logging

from models.model_asignacion_externa import AsignacionExterna
from services.external_sync_service import get_external_sync_service, SyncStatus

logger = logging.getLogger(__name__)


class PosicionesService:
    """Servicio para gestionar posiciones GPS."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._config = get_app_config()

    async def _validar_asignacion_en_curso(
        self, id_asignacion: int, id_usuario: int | None = None
    ) -> AsignacionRutas:
        """Valida que la asignación exista y esté en curso."""
        result = await self.db.execute(
            select(AsignacionRutas).where(
                AsignacionRutas.id_asignacion == id_asignacion
            )
        )
        asignacion = result.scalar_one_or_none()

        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la asignación con id {id_asignacion}.",
            )

        if asignacion.estado != EstadoAsignacion.en_curso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación {id_asignacion} no está en curso. "
                f"Estado actual: {asignacion.estado.value}",
            )

        return asignacion

    async def registrar_posicion(
        self,
        id_asignacion: int,
        data: PosicionCreate,
    ) -> PosicionResponse:
        """Registra una nueva posición GPS."""
        logger.info(
            f"Registrando posición para asignación {id_asignacion}: lat={data.latitud}, lon={data.longitud}, timestamp={data.timestamp}"
        )

        # Validar asignación
        await self._validar_asignacion_en_curso(id_asignacion)

        # Crear posición
        try:
            posicion = RecorridoPosicion(
                id_asignacion=id_asignacion,
                latitud=data.latitud,
                longitud=data.longitud,
                accuracy=data.accuracy,
                speed=data.speed,
                bearing=data.bearing,
                timestamp=data.timestamp,
            )

            self.db.add(posicion)
            await self.db.flush()
            await self.db.refresh(posicion)
            logger.info(f"Posición registrada exitosamente con ID {posicion.id}")
        except Exception as e:
            logger.error(f"Error al crear posición en BD: {str(e)}", exc_info=True)
            raise

        # Notificar por WebSocket a los administradores
        await ws_manager.broadcast(
            id_asignacion,
            {
                "evento": "posicion_actualizada",
                "id_asignacion": id_asignacion,
                "latitud": float(data.latitud),
                "longitud": float(data.longitud),
                "timestamp": data.timestamp.isoformat(),
                "data": {  # Respaldo para compatibilidad
                    "lat": float(data.latitud),
                    "lon": float(data.longitud),
                },
            },
        )

        # Enviar posición a la API externa
        print(f"[DEBUG POSICION] Iniciando sincronización de posición para asignación {id_asignacion}")
        try:
            result_ext = await self.db.execute(
                select(AsignacionExterna).where(
                    AsignacionExterna.id_asignacion == id_asignacion
                )
            )
            asignacion_externa = result_ext.scalar_one_or_none()
            print(f"[DEBUG POSICION] asignacion_externa: {asignacion_externa}")

            if asignacion_externa and asignacion_externa.recorrido_externo_id:
                print(f"[DEBUG POSICION] recorrido_externo_id: {asignacion_externa.recorrido_externo_id}")
                sync_service = get_external_sync_service()
                print(f"[DEBUG POSICION] sync_service creado: {sync_service}")
                print(f"[DEBUG POSICION] api_base_url: {sync_service.api_base_url}")
                print(f"[DEBUG POSICION] perfil_id: {sync_service.perfil_id}")
                
                habilitada = sync_service.es_sincronizacion_habilitada()
                print(f"[DEBUG POSICION] es_sincronizacion_habilitada() = {habilitada}")
                
                if habilitada:
                    try:
                        print(f"[SYNC POSICION] Enviando posición a API externa...")
                        metadata = await sync_service.sync_create_posicion(
                            recorrido_externo_id=asignacion_externa.recorrido_externo_id,
                            latitud=float(data.latitud),
                            longitud=float(data.longitud),
                            perfil_id=None,  # Usa el configurado por defecto dinámicamente
                            recurso_id_local=posicion.id,
                        )
                        print(f"[DEBUG POSICION] metadata recibida: estado={metadata.estado}, error={metadata.error_message}")
                        if metadata.estado != SyncStatus.SUCCESS:
                            logger.warning(
                                f"[SYNC] Error al sincronizar posición en asignación {id_asignacion}: {metadata.error_message}"
                            )
                        else:
                            print(f"[SYNC POSICION ✅] Posición enviada exitosamente")
                    except Exception as e:
                        logger.error(
                            f"[SYNC ERROR] Error inesperado sincronizando posición: {str(e)}"
                        )
                        print(f"[SYNC POSICION ❌] Error: {e}")
                else:
                    print(f"[SYNC POSICION SKIP] Sincronización deshabilitada")
            else:
                print(f"[DEBUG POSICION] No hay asignacion_externa o recorrido_externo_id")
        except Exception as e:
            logger.error(
                f"Error al reenviar posición a la API externa para asignación {id_asignacion}: {str(e)}"
            )
            print(f"[DEBUG POSICION] Error general: {e}")
            # No lanzamos excepción para no romper el flujo principal si la API externa falla

        return PosicionResponse.model_validate(posicion)

    async def listar_posiciones(
        self,
        id_asignacion: int,
        page: int = 1,
        page_size: int = 50,
    ) -> PosicionListResponse:
        """Lista posiciones con paginación."""
        # Validar que la asignación exista
        result = await self.db.execute(
            select(AsignacionRutas).where(
                AsignacionRutas.id_asignacion == id_asignacion
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la asignación con id {id_asignacion}.",
            )

        # Contar total
        count_result = await self.db.execute(
            select(func.count())
            .select_from(RecorridoPosicion)
            .where(RecorridoPosicion.id_asignacion == id_asignacion)
        )
        total = count_result.scalar() or 0

        # Calcular paginación
        offset = (page - 1) * page_size
        has_next = (offset + page_size) < total
        has_prev = page > 1

        # Obtener posiciones
        result = await self.db.execute(
            select(RecorridoPosicion)
            .where(RecorridoPosicion.id_asignacion == id_asignacion)
            .order_by(desc(RecorridoPosicion.timestamp))
            .offset(offset)
            .limit(page_size)
        )
        posiciones = result.scalars().all()

        return PosicionListResponse(
            items=[PosicionResponse.model_validate(p) for p in posiciones],
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_prev=has_prev,
        )

    async def obtener_ultima_posicion(
        self,
        id_asignacion: int,
    ) -> Optional[PosicionResponse]:
        """Obtiene la última posición registrada."""
        result = await self.db.execute(
            select(RecorridoPosicion)
            .where(RecorridoPosicion.id_asignacion == id_asignacion)
            .order_by(desc(RecorridoPosicion.timestamp))
            .limit(1)
        )
        posicion = result.scalar_one_or_none()

        if posicion:
            return PosicionResponse.model_validate(posicion)
        return None

    def _validar_imagen_base64(self, imagen_base64: str) -> tuple[bytes, str]:
        """Valida y extrae los datos de la imagen base64.
        Acepta base64 con o sin prefijo data:image/...;base64,.

        Returns:
            tuple: (bytes de la imagen, extensión del archivo)
        """
        # Patrón para validar formato data URL de imagen
        pattern = r"^data:image/([a-z]+);base64,"
        match = re.match(pattern, imagen_base64)

        if match:
            # Tiene prefijo data URL
            tipo_imagen = match.group(1)
            extension = "jpg" if tipo_imagen == "jpeg" else tipo_imagen
            # Extraer los datos base64
            datos_base64 = imagen_base64.split(",", 1)[1]
        else:
            # Base64 puro sin prefijo
            datos_base64 = imagen_base64
            extension = "webp"  # Por defecto, se detectará después

        try:
            datos_imagen = base64.b64decode(datos_base64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error al decodificar la imagen base64: {str(e)}",
            )

        # Validar tamaño máximo (5MB antes de codificar)
        max_size_bytes = 5 * 1024 * 1024  # 5MB
        if len(datos_imagen) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"La imagen excede el tamaño máximo de 5MB. Tamaño actual: {len(datos_imagen) / (1024*1024):.2f}MB",
            )

        # Validar que sea una imagen válida (primeros bytes)
        firmas_validas = {
            b"\xff\xd8\xff": "jpg",
            b"\x89PNG": "png",
            b"GIF87a": "gif",
            b"GIF89a": "gif",
            b"RIFF": "webp",
        }

        es_valida = False
        detected_extension = extension
        for firma, ext in firmas_validas.items():
            if datos_imagen.startswith(firma):
                es_valida = True
                detected_extension = ext
                break

        if not es_valida:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Los datos no corresponden a una imagen válida. Formatos aceptados: JPEG, PNG, WEBP.",
            )

        # Validar formatos aceptados
        if detected_extension not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Formato de imagen no soportado: {detected_extension}. Formatos aceptados: JPEG, PNG, WEBP.",
            )

        return datos_imagen, detected_extension

    def _procesar_imagen(self, datos_imagen: bytes, max_size: int = 512) -> bytes:
        """Procesa la imagen: redimensiona y convierte a WEBP.

        Args:
            datos_imagen: Bytes de la imagen original
            max_size: Tamaño máximo del lado más largo (default: 512px)

        Returns:
            bytes: Imagen procesada en formato WEBP
        """
        try:
            # Abrir la imagen desde bytes
            imagen = Image.open(BytesIO(datos_imagen))

            # Convertir a RGB si es necesario (WEBP no soporta RGBA con transparencia)
            if imagen.mode in ("RGBA", "LA", "P"):
                imagen = imagen.convert("RGB")

            # Obtener dimensiones actuales
            ancho, alto = imagen.size

            # Calcular nuevo tamaño manteniendo aspect ratio
            if ancho > alto:
                if ancho > max_size:
                    nuevo_alto = int(alto * (max_size / ancho))
                    nuevo_ancho = max_size
                else:
                    nuevo_ancho = ancho
                    nuevo_alto = alto
            else:
                if alto > max_size:
                    nuevo_ancho = int(ancho * (max_size / alto))
                    nuevo_alto = max_size
                else:
                    nuevo_ancho = ancho
                    nuevo_alto = alto

            # Redimensionar usando LANCZOS para mejor calidad
            if nuevo_ancho != ancho or nuevo_alto != alto:
                imagen = imagen.resize(
                    (nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS
                )

            # Guardar en formato WEBP
            output = BytesIO()
            imagen.save(output, format="WEBP", quality=85)
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error al procesar imagen: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno al procesar la imagen: {str(e)}",
            )

    async def _guardar_imagen_posicion(
        self,
        datos_imagen: bytes,
        posicion_uuid: str,
    ) -> tuple[str, str]:
        """Guarda la imagen de una posición en el sistema de archivos.

        Args:
            datos_imagen: Bytes de la imagen procesada
            posicion_uuid: UUID de la posición

        Returns:
            tuple: (ruta relativa, URL completa)
        """
        # Crear directorio para posiciones si no existe
        upload_dir = getattr(self._config, "upload_dir", "uploads/fotos")
        posiciones_dir = os.path.join(os.path.dirname(upload_dir), "posiciones")
        os.makedirs(posiciones_dir, exist_ok=True)

        # Generar nombre de archivo
        nombre_archivo = f"{posicion_uuid}.webp"
        ruta_archivo = os.path.join(posiciones_dir, nombre_archivo)

        # Guardar archivo
        with open(ruta_archivo, "wb") as f:
            f.write(datos_imagen)

        # Retornar ruta relativa y URL
        ruta_relativa = f"posiciones/{nombre_archivo}"

        # Obtener base URL de la configuración o usar localhost por defecto
        base_url = getattr(self._config, "base_url", "http://localhost:8000")
        url = f"{base_url}/storage/posiciones/{nombre_archivo}"

        return ruta_relativa, url

    async def registrar_imagen_posicion(
        self,
        posicion_uuid: str,
        imagen_base64: str,
    ) -> PosicionImagenResponse:
        """Registra o actualiza la imagen de una posición.

        Args:
            posicion_uuid: UUID de la posición
            imagen_base64: Imagen en formato base64

        Returns:
            PosicionImagenResponse con la información de la imagen guardada
        """
        # Validar y decodificar imagen
        datos_imagen, _ = self._validar_imagen_base64(imagen_base64)

        # Procesar imagen (redimensionar y convertir a WEBP)
        datos_procesados = self._procesar_imagen(datos_imagen)

        # Buscar la posición por UUID
        result = await self.db.execute(
            select(RecorridoPosicion).where(RecorridoPosicion.uuid == posicion_uuid)
        )
        posicion = result.scalar_one_or_none()

        if not posicion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La posición indicada no existe.",
            )

        # Validar que la asignación esté en curso
        await self._validar_asignacion_en_curso(posicion.id_asignacion)

        # Guardar imagen
        ruta_relativa, url = await self._guardar_imagen_posicion(
            datos_procesados, posicion_uuid
        )

        # Actualizar el campo imagen en la posición
        posicion.imagen = ruta_relativa
        await self.db.flush()
        await self.db.refresh(posicion)

        # Sincronización con API externa
        try:
            result_ext = await self.db.execute(
                select(AsignacionExterna).where(
                    AsignacionExterna.id_asignacion == posicion.id_asignacion
                )
            )
            asignacion_externa = result_ext.scalar_one_or_none()

            if asignacion_externa and asignacion_externa.recorrido_externo_id:
                sync_service = get_external_sync_service()
                if sync_service.es_sincronizacion_habilitada():
                    # La API externa requiere que el lado mayor no supere los 256px
                    datos_imagen_original, _ = self._validar_imagen_base64(imagen_base64)
                    datos_procesados_ext = self._procesar_imagen(datos_imagen_original, max_size=256)
                    
                    # Codificar en base64 con prefijo MIME para el envío externo
                    imagen_ext_b64 = base64.b64encode(datos_procesados_ext).decode('utf-8')
                    payload_ext = f"data:image/webp;base64,{imagen_ext_b64}"

                    logger.info(f"[SYNC IMAGE] Sincronizando imagen de posición {posicion_uuid} con API externa")
                    if hasattr(sync_service, 'sync_upload_image_posicion'):
                        await sync_service.sync_upload_image_posicion(
                            posicion_uuid=posicion_uuid,
                            imagen_base64=payload_ext
                        )
        except Exception as e:
            logger.error(f"Error al sincronizar imagen con API externa para posición {posicion_uuid}: {str(e)}")

        return PosicionImagenResponse(
            posicion_id=posicion_uuid, imagen=ruta_relativa, url=url
        )

    async def obtener_posiciones_activas(self) -> list[dict]:
        """Obtiene las posiciones más recientes de todos los vehículos activos en ruta."""
        # Obtener asignaciones en curso
        result = await self.db.execute(
            select(AsignacionRutas).where(
                AsignacionRutas.estado == EstadoAsignacion.en_curso
            )
        )
        asignaciones_activas = result.scalars().all()

        posiciones_activas = []

        for asignacion in asignaciones_activas:
            # Obtener la última posición de cada asignación
            result_pos = await self.db.execute(
                select(RecorridoPosicion)
                .where(RecorridoPosicion.id_asignacion == asignacion.id_asignacion)
                .order_by(desc(RecorridoPosicion.timestamp))
                .limit(1)
            )
            posicion = result_pos.scalar_one_or_none()

            if posicion:
                posiciones_activas.append(
                    {
                        "id_asignacion": asignacion.id_asignacion,
                        "id_vehiculo": asignacion.id_vehiculo,
                        "id_ruta": asignacion.id_ruta,
                        "latitud": posicion.latitud,
                        "longitud": posicion.longitud,
                        "timestamp": posicion.timestamp,
                        "speed": posicion.speed,
                        "bearing": posicion.bearing,
                        "accuracy": posicion.accuracy,
                    }
                )

        return posiciones_activas
