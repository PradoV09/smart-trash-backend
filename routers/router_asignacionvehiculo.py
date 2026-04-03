# routers/router_asignacionvehiculo.py

from fastapi import APIRouter, status
from schemas.schema_asignaciovehiculo import AsignacionCreate, AsignacionResponse, AsignacionPublicResponse
from schemas.schema_responses import SuccessResponse
from schemas.schema_tripulacionasignada import TripulacionCreate, TripulacionResponse
from controllers import controller_asignaciovehiculo

# Admin
router_admin = APIRouter(prefix="/admin/asignaciones", tags=["Asignaciones - Admin"])

router_admin.post("/",                                        response_model=SuccessResponse[AsignacionResponse], status_code=status.HTTP_201_CREATED)(controller_asignaciovehiculo.crear_asignacion)
router_admin.get("/",                                         response_model=SuccessResponse[list[AsignacionResponse]])(controller_asignaciovehiculo.listar_asignaciones)
router_admin.get("/rutas/{id_ruta}",                          response_model=SuccessResponse[dict])(controller_asignaciovehiculo.obtener_detalles_ruta)
router_admin.get("/{id_asignacion}",                          response_model=SuccessResponse[AsignacionResponse])(controller_asignaciovehiculo.obtener_asignacion_admin)
router_admin.post("/{id_asignacion}/cancelar",                response_model=SuccessResponse[AsignacionResponse])(controller_asignaciovehiculo.cancelar_asignacion)
router_admin.post("/{id_asignacion}/tripulacion",             response_model=SuccessResponse[TripulacionResponse], status_code=status.HTTP_201_CREATED)(controller_asignaciovehiculo.agregar_miembro_tripulacion)
router_admin.delete("/{id_asignacion}/tripulacion/{id_usuario}", response_model=SuccessResponse[dict[str, int]])(controller_asignaciovehiculo.eliminar_miembro_tripulacion)


# Driver
router_driver = APIRouter(prefix="/driver/asignaciones", tags=["Asignaciones - Driver"])

router_driver.get("/{id_asignacion}",           response_model=SuccessResponse[AsignacionResponse])(controller_asignaciovehiculo.ver_asignacion_driver)
router_driver.post("/{id_asignacion}/iniciar",  response_model=SuccessResponse[AsignacionResponse])(controller_asignaciovehiculo.iniciar_recorrido)
router_driver.post("/{id_asignacion}/finalizar", response_model=SuccessResponse[AsignacionResponse])(controller_asignaciovehiculo.finalizar_recorrido)

# Recolector
router_recolector = APIRouter(prefix="/recolector/asignaciones", tags=["Asignaciones - Recolector"])

router_recolector.get("/{id_asignacion}",                              response_model=SuccessResponse[AsignacionResponse])(controller_asignaciovehiculo.ver_asignacion_recolector)
router_recolector.post("/{id_asignacion}/confirmar/{id_usuario}",      response_model=SuccessResponse[TripulacionResponse])(controller_asignaciovehiculo.confirmar_participacion)

# User ciudadano
router_user = APIRouter(prefix="/rutas", tags=["Rutas - Ciudadano"])

router_user.get("/{id_ruta}/horario", response_model=SuccessResponse[AsignacionPublicResponse])(controller_asignaciovehiculo.ver_horario_ruta)