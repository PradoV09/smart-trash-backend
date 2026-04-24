"""Router para gestión de fotos/evidencia del recorrido.

Endpoints:
- POST /api/asignaciones/{id}/fotos - Registrar foto (driver)
- GET /admin/asignaciones/{id}/fotos - Listar fotos (admin)
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
    status_code=status.HTTP_201_CREATED
)(controller_fotos.registrar_foto)


# Router para admin - listar fotos
router_admin = APIRouter(prefix="/admin/asignaciones", tags=["Admin: Fotos"])

router_admin.get(
    "/{id_asignacion:int}/fotos",
    response_model=SuccessResponse[FotoListResponse]
)(controller_fotos.listar_fotos_admin)