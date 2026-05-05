"""Router para integración de rutas con API externa."""

from fastapi import APIRouter, Query, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from controllers import controller_rutas, controller_asignacionrutas
from core.dependecies import get_db
from schemas.schema_responses import SuccessResponse
from schemas.schema_rutas_externas import RutasCreateRequest, RutasCreateResponse, RutaResponse
from schemas.schema_asignacionrutas import AsignacionPublicResponse


router = APIRouter(prefix="/rutas", tags=["Integración: Rutas Externas"])
router_public = APIRouter(prefix="/publico/rutas", tags=["Público: Rutas"])

# --- Public Routes ---
@router_public.get("/activas", response_model=SuccessResponse[list[AsignacionPublicResponse]])
async def listar_asignaciones_activas(db: AsyncSession = Depends(get_db)):
    """Lista las rutas que tienen un camión en movimiento actualmente."""
    return await controller_asignacionrutas.listar_asignaciones_en_curso_publico(db)

@router_public.get("/{id_ruta}/horario", response_model=SuccessResponse[AsignacionPublicResponse])
async def obtener_horario_ruta(id_ruta: str, db: AsyncSession = Depends(get_db)):
    """Consulta el horario y estado de una ruta específica."""
    return await controller_asignacionrutas.ver_horario_ruta(id_ruta, db)

# --- Integration Routes ---

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
