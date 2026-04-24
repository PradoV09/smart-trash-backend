"""Router para gestión de posiciones GPS del recorrido.

Endpoints:
- POST /api/asignaciones/{id}/posiciones - Registrar posición (driver)
- GET /admin/asignaciones/{id}/posiciones - Listar posiciones (admin)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, DriverDep, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_posiciones import (
    PosicionCreate,
    PosicionResponse,
    PosicionListResponse,
)
from controllers import controller_posiciones

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