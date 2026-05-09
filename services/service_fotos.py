"""Servicio para gestión de fotos/evidencia del recorrido."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from datetime import datetime, timezone
import base64
import uuid
import os
import re

from models.model_fotos import RecorridoFoto, TipoFoto
from models.model_asignacionrutas import AsignacionRutas, EstadoAsignacion
from schemas.schema_fotos import (
    FotoCreate,
    FotoResponse,
    FotoListResponse,
)
from core.websocket_manager import ws_manager
from core.config import get_app_config


class FotosService:
    """Servicio para gestionar fotos/evidencia."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._config = get_app_config()

    async def _validar_asignacion_en_curso(
        self,
        id_asignacion: int,
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

    def _validar_imagen_base64(self, imagen_base64: str) -> tuple[bytes, str]:
        """Valida y extrae los datos de la imagen base64.

        Returns:
            tuple: (bytes de la imagen, extensión del archivo)
        """
        # Patrón para validar formato data URL de imagen
        pattern = r"^data:image/([a-z]+);base64,"
        match = re.match(pattern, imagen_base64)

        if not match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El formato de imagen debe ser 'data:image/<tipo>;base64,<datos>' "
                "(ej: data:image/jpeg;base64,...)",
            )

        tipo_imagen = match.group(1)
        extension = "jpg" if tipo_imagen == "jpeg" else tipo_imagen

        # Extraer los datos base64
        datos_base64 = imagen_base64.split(",", 1)[1]

        try:
            datos_imagen = base64.b64decode(datos_base64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al decodificar la imagen base64: {str(e)}",
            )

        # Validar que sea una imagen válida (primeros bytes)
        # Firmas comunes de imágenes
        firmas_validas = {
            b"\xff\xd8\xff": "jpg",  # JPEG
            b"\x89PNG": "png",  # PNG
            b"GIF87a": "gif",  # GIF87a
            b"GIF89a": "gif",  # GIF89a
            b"RIFF": "webp",  # WebP
        }

        es_valida = False
        for firma, ext in firmas_validas.items():
            if datos_imagen.startswith(firma):
                es_valida = True
                break

        if not es_valida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los datos no corresponden a una imagen válida.",
            )

        return datos_imagen, extension

    async def _guardar_imagen(
        self,
        datos_imagen: bytes,
        extension: str,
        id_asignacion: int,
    ) -> str:
        """Guarda la imagen en el sistema de archivos.

        Returns:
            str: URL de acceso a la imagen
        """
        # Crear directorio si no existe
        upload_dir = getattr(self._config, "upload_dir", "uploads/fotos")
        os.makedirs(upload_dir, exist_ok=True)

        # Generar nombre único
        nombre_archivo = f"{id_asignacion}_{uuid.uuid4().hex}.{extension}"
        ruta_archivo = os.path.join(upload_dir, nombre_archivo)

        # Guardar archivo
        with open(ruta_archivo, "wb") as f:
            f.write(datos_imagen)

        # Retornar URL (con prefijo /api ya que el router está bajo /api)
        return f"/api/uploads/fotos/{nombre_archivo}"

    async def registrar_foto(
        self,
        id_asignacion: int,
        data: FotoCreate,
    ) -> FotoResponse:
        """Registra una nueva foto/evidencia."""
        # Validar asignación
        await self._validar_asignacion_en_curso(id_asignacion)

        # Validar y decodificar imagen
        datos_imagen, extension = self._validar_imagen_base64(data.imagen_base64)

        # Guardar imagen
        url = await self._guardar_imagen(datos_imagen, extension, id_asignacion)

        # Convertir tipo string a enum
        try:
            tipo_foto = TipoFoto(data.tipo)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de foto inválido: {data.tipo}. "
                f"Valores válidos: {[t.value for t in TipoFoto]}",
            )

        # Crear registro en BD
        foto = RecorridoFoto(
            id_asignacion=id_asignacion,
            url=url,
            tipo=tipo_foto,
            timestamp_captura=data.timestamp,
        )

        self.db.add(foto)
        await self.db.flush()
        await self.db.refresh(foto)

        # Notificar por WebSocket
        await ws_manager.broadcast(
            id_asignacion,
            {
                "evento": "foto_registrada",
                "id_asignacion": id_asignacion,
                "tipo": data.tipo,
                "timestamp": data.timestamp.isoformat(),
            },
        )

        return FotoResponse.model_validate(foto)

    async def listar_fotos(
        self,
        id_asignacion: int,
    ) -> FotoListResponse:
        """Lista todas las fotos de una asignación."""
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
            .select_from(RecorridoFoto)
            .where(RecorridoFoto.id_asignacion == id_asignacion)
        )
        total = count_result.scalar() or 0

        # Obtener fotos
        result = await self.db.execute(
            select(RecorridoFoto)
            .where(RecorridoFoto.id_asignacion == id_asignacion)
            .order_by(RecorridoFoto.timestamp_captura.desc())
        )
        fotos = result.scalars().all()

        return FotoListResponse(
            items=[FotoResponse.model_validate(f) for f in fotos],
            total=total,
        )
