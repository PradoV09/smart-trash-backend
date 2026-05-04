# routers/router_asignacionrutas.py

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db
from schemas.schema_asignacionrutas import AsignacionCreate, AsignacionResponse, AsignacionPublicResponse
from schemas.schema_responses import SuccessResponse
from controllers import controller_asignacionrutas

# Admin
router_admin = APIRouter(prefix="/admin/asignaciones", tags=["Admin: Asignaciones"])

router_admin.post("",                                        response_model=SuccessResponse[AsignacionResponse], status_code=status.HTTP_201_CREATED)(controller_asignacionrutas.crear_asignacion)
router_admin.get("",                                         response_model=SuccessResponse[list[AsignacionResponse]])(controller_asignacionrutas.listar_asignaciones)
router_admin.get("/rutas/{id_ruta}",                          response_model=SuccessResponse[dict])(controller_asignacionrutas.obtener_detalles_ruta)
router_admin.get("/{id_asignacion:int}",                      response_model=SuccessResponse[AsignacionResponse])(controller_asignacionrutas.obtener_asignacion_admin)
router_admin.post("/{id_asignacion}/cancelar",                response_model=SuccessResponse[AsignacionResponse])(controller_asignacionrutas.cancelar_asignacion)
router_admin.post("/{id_asignacion}/validar-piloto",          response_model=SuccessResponse[dict])(controller_asignacionrutas.validar_tripulacion_con_piloto)

# Driver
router_driver = APIRouter(prefix="/driver/asignaciones", tags=["Driver: Asignaciones"])

router_driver.get("",                           response_model=SuccessResponse[list[AsignacionResponse]])(controller_asignacionrutas.listar_asignaciones_driver)
router_driver.get("/{id_asignacion}",           response_model=SuccessResponse[AsignacionResponse])(controller_asignacionrutas.ver_asignacion_driver)
router_driver.post("/{id_asignacion}/iniciar",  response_model=SuccessResponse[AsignacionResponse])(controller_asignacionrutas.iniciar_recorrido)
router_driver.post("/{id_asignacion}/finalizar", response_model=SuccessResponse[AsignacionResponse])(controller_asignacionrutas.finalizar_recorrido)

# User ciudadano (Público)
router_user = APIRouter(prefix="/api/publico/rutas", tags=["Público: Rutas"])

@router_user.get("/activas", response_model=SuccessResponse[list[AsignacionPublicResponse]])
async def listar_asignaciones_activas(db: AsyncSession = Depends(get_db)):
    """Lista las rutas que tienen un camión en movimiento actualmente."""
    return await controller_asignacionrutas.listar_asignaciones_en_curso_publico(db)

@router_user.get("/{id_ruta}/horario", response_model=SuccessResponse[AsignacionPublicResponse])
async def obtener_horario_ruta(id_ruta: str, db: AsyncSession = Depends(get_db)):
    """Consulta el horario y estado de una ruta específica."""
    return await controller_asignacionrutas.ver_horario_ruta(id_ruta, db)