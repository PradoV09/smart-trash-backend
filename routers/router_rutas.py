"""Router para integración de rutas con API externa."""

from fastapi import APIRouter, status

from controllers import controller_rutas
from schemas.schema_responses import SuccessResponse
from schemas.schema_rutas_externas import RutasCreateRequest, RutasCreateResponse


router = APIRouter(prefix="/api/rutas", tags=["Integración: Rutas Externas"])

router.post(
    "",
    response_model=SuccessResponse[RutasCreateResponse],
    status_code=status.HTTP_201_CREATED,
)(controller_rutas.crear_ruta)
