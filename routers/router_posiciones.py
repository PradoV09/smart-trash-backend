"""Router para gestión de posiciones GPS del recorrido.

Endpoints:
- POST /api/asignaciones/{id}/posiciones - Registrar posición (driver)
- GET /admin/asignaciones/{id}/posiciones - Listar posiciones (admin)
- POST /api/posiciones/{posicion_id}/imagen - Registrar/actualizar imagen de posición (driver)
- GET /api/uploads/posiciones/{filename} - Obtener archivo de imagen de posición
"""

from fastapi import APIRouter, Depends, status, Path, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, DriverDep, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_posiciones import (
    PosicionCreate,
    PosicionResponse,
    PosicionListResponse,
    PosicionImagenCreate,
    PosicionImagenResponse,
)
from controllers import controller_posiciones
import os
import logging

# Router para driver - registrar posiciones
router_driver = APIRouter(prefix="/driver/asignaciones", tags=["Driver: Posiciones"])

router_driver.post(
    "/{id_asignacion:int}/posiciones",
    response_model=SuccessResponse[PosicionResponse],
    status_code=status.HTTP_201_CREATED
)(controller_posiciones.registrar_posicion)


# Router para admin - listar posiciones
router_admin = APIRouter(prefix="/admin/asignaciones", tags=["Admin: Posiciones"])

router_admin.get(
    "/{id_asignacion:int}/posiciones",
    response_model=SuccessResponse[PosicionListResponse]
)(controller_posiciones.listar_posiciones_admin)

router_admin.get(
    "/{id_asignacion:int}/posiciones/ultima",
    response_model=SuccessResponse[PosicionResponse | None]
)(controller_posiciones.obtener_ultima_posicion)

router_admin.get(
    "/posiciones/activas",
    response_model=SuccessResponse,
    summary="Obtener posiciones activas de vehículos en ruta",
    description="Retorna las posiciones más recientes de todos los vehículos que están actualmente en ruta (estado 'en_curso')"
)(controller_posiciones.obtener_posiciones_activas)


# Router para driver - registrar/actualizar imagen de posición
router_imagen = APIRouter(prefix="/api/recorridos/posiciones", tags=["Driver: Imagen Posición"])

router_imagen.post(
    "/{posicion_id}/imagen",
    response_model=SuccessResponse[PosicionImagenResponse],
    status_code=status.HTTP_200_OK,
    summary="Registrar o actualizar imagen de posición",
    description="Permite registrar o actualizar la imagen asociada a una posición específica de un recorrido. La imagen se recibe en formato Base64 (con o sin prefijo data:image/...;base64,), se valida que no supere los 5MB, se procesa para que su lado mayor no supere los 512px, se mantiene la proporción original y se almacena en formato WEBP con calidad 85. Solo se permite la operación si el recorrido asociado se encuentra en estado En Curso."
)(controller_posiciones.registrar_imagen_posicion)


# Router público para acceder a los archivos de imagen de posición
router_public = APIRouter(prefix="/api/uploads/posiciones", tags=["Archivos: Imágenes Posición"])

logger = logging.getLogger(__name__)


async def obtener_imagen_posicion_archivo(
    filename: str = Path(..., description="Nombre del archivo de imagen")
) -> FileResponse:
    """Obtiene y sirve un archivo de imagen de posición.

    Args:
        filename: Nombre del archivo (ej: 3fa85f64-5717-4562-b3fc-2c963f66afa6.webp)

    Returns:
        FileResponse con el archivo de imagen
    """
    try:
        upload_dir = "uploads"
        posiciones_dir = os.path.join(upload_dir, "posiciones")

        # Validar que el filename no contenga caracteres peligrosos
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo inválido.",
            )

        filepath = os.path.join(posiciones_dir, filename)

        # Verificar que el archivo existe
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            logger.warning(f"Intento de acceso a imagen de posición inexistente: {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo de imagen no encontrado.",
            )

        # Determinar el tipo MIME según la extensión
        ext = os.path.splitext(filename)[1].lower()
        media_types = {
            ".webp": "image/webp",
        }
        media_type = media_types.get(ext, "application/octet-stream")

        # Retornar el archivo
        return FileResponse(path=filepath, media_type=media_type, filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al servir imagen de posición {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el archivo de imagen.",
        )


router_public.get(
    "/{filename}",
    responses={
        200: {
            "content": {
                "image/webp": {},
            }
        }
    },
    summary="Obtener archivo de imagen de posición",
    description="Sirve un archivo de imagen de posición almacenado en el servidor. Accesible sin autenticación.",
)(obtener_imagen_posicion_archivo)