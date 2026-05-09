"""Controladores para gestión de fotos/evidencia del recorrido."""

from fastapi import Depends, HTTPException, status, File, Path
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, DriverDep, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_fotos import FotoCreate, FotoResponse, FotoListResponse
from models.model_usuarios import Usuario
from services.service_fotos import FotosService
import logging
import os
from core.config import get_app_config

logger = logging.getLogger(__name__)


async def registrar_foto(
    id_asignacion: int,
    data: FotoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> SuccessResponse[FotoResponse]:
    """Registra una nueva foto/evidencia para una asignación."""
    try:
        service = FotosService(db)
        foto = await service.registrar_foto(id_asignacion, data)
        return success_response(data=foto, message="Foto registrada exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar foto en asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al registrar la foto: {str(e)}",
        )


async def listar_fotos_admin(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[FotoListResponse]:
    """Lista todas las fotos de una asignación."""
    try:
        service = FotosService(db)
        result = await service.listar_fotos(id_asignacion)
        return success_response(data=result, message="Fotos obtenidas exitosamente.")
    except Exception as e:
        logger.error(f"Error al listar fotos de asignación {id_asignacion}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar la lista de fotos.",
        )


async def obtener_foto_archivo(
    filename: str = Path(..., description="Nombre del archivo de foto")
) -> FileResponse:
    """Obtiene y sirve un archivo de foto.

    Args:
        filename: Nombre del archivo (ej: 11_02471979b9c943258ec535572da65e1f.png)

    Returns:
        FileResponse con el archivo de imagen
    """
    try:
        config = get_app_config()
        upload_dir = getattr(config, "upload_dir", "uploads/fotos")

        # Validar que el filename no contenga caracteres peligrosos
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo inválido.",
            )

        filepath = os.path.join(upload_dir, filename)

        # Verificar que el archivo existe
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            logger.warning(f"Intento de acceso a foto inexistente: {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo de foto no encontrado.",
            )

        # Determinar el tipo MIME según la extensión
        ext = os.path.splitext(filename)[1].lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_types.get(ext, "application/octet-stream")

        # Retornar el archivo
        return FileResponse(path=filepath, media_type=media_type, filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al servir foto {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el archivo de foto.",
        )
