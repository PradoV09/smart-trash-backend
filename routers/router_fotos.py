"""Router para gestión de fotos/evidencia del recorrido.

Endpoints:
- POST /api/asignaciones/{id}/fotos - Registrar foto (driver)
- GET /admin/asignaciones/{id}/fotos - Listar fotos (admin)
- GET /uploads/fotos/{filename} - Obtener archivo de foto
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, DriverDep, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_fotos import (
    FotoCreate,
    FotoResponse,
    FotoListResponse,
)
from controllers import controller_fotos

# Router para driver - registrar fotos
router_driver = APIRouter(prefix="/driver/asignaciones", tags=["Driver: Fotos"])

router_driver.post(
    "/{id_asignacion:int}/fotos",
    response_model=SuccessResponse[FotoResponse],
    status_code=status.HTTP_201_CREATED,
)(controller_fotos.registrar_foto)


# Router para admin - listar fotos
router_admin = APIRouter(prefix="/admin/asignaciones", tags=["Admin: Fotos"])

router_admin.get(
    "/{id_asignacion:int}/fotos", response_model=SuccessResponse[FotoListResponse]
)(controller_fotos.listar_fotos_admin)


# Router público para acceder a los archivos de foto
router_public = APIRouter(prefix="/uploads/fotos", tags=["Archivos: Fotos"])

router_public.get(
    "/{filename}",
    responses={
        200: {
            "content": {
                "image/jpeg": {},
                "image/png": {},
                "image/gif": {},
                "image/webp": {},
            }
        }
    },
    summary="Obtener archivo de foto",
    description="Sirve un archivo de foto almacenado en el servidor. Accesible sin autenticación.",
)(controller_fotos.obtener_foto_archivo)


# Router para manejar URLs antiguas con doble /api (backward compatibility)
router_legacy = APIRouter(
    prefix="/api/uploads/fotos", tags=["Archivos: Fotos (Legacy)"]
)

router_legacy.get(
    "/{filename}",
    responses={
        200: {
            "content": {
                "image/jpeg": {},
                "image/png": {},
                "image/gif": {},
                "image/webp": {},
            }
        }
    },
    summary="Obtener archivo de foto (Legacy)",
    description="Endpoint legacy para URLs antiguas con /api duplicado. Accesible sin autenticación.",
)(controller_fotos.obtener_foto_archivo)
