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

# User ciudadano (Público) - MOVED TO router_rutas.py
# (The public routes were moved to consolidate route-related endpoints)