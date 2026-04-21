"""Router para integración de rutas con API externa."""

from fastapi import APIRouter, Query, status

from controllers import controller_rutas
from schemas.schema_responses import SuccessResponse
from schemas.schema_rutas_externas import RutasCreateRequest, RutasCreateResponse, RutaResponse


router = APIRouter(prefix="/api/rutas", tags=["Integración: Rutas Externas"])

router.post(
    "",
    response_model=SuccessResponse[RutasCreateResponse],
    status_code=status.HTTP_201_CREATED,
)(controller_rutas.crear_ruta)


@router.get(
    "",
    response_model=SuccessResponse[list[RutaResponse] | RutaResponse],
    status_code=status.HTTP_200_OK,
)
async def listar_rutas(perfil_id: str | None = Query(default=None, description="UUID del perfil")):
    return await controller_rutas.listar_rutas(perfil_id)

@router.get(
    "/{id}",
    response_model=SuccessResponse[RutaResponse],
    status_code=status.HTTP_200_OK,
)
async def obtener_ruta(id: str, perfil_id: str | None = Query(default=None, description="UUID del perfil")):
    return await controller_rutas.obtener_ruta(id, perfil_id)
