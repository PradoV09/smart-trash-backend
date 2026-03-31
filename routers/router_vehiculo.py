# routers/router_vehiculo.py

from fastapi import APIRouter, status
from schemas.schema_responses import SuccessResponse
from schemas.schema_vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from models.model_vehiculo import EstadoVehiculo
from controllers import controller_vehiculo

router = APIRouter(prefix="/admin/vehiculos", tags=["Vehículos"])

router.post("/",                      response_model=SuccessResponse[VehiculoResponse], status_code=status.HTTP_201_CREATED)(controller_vehiculo.crear_vehiculo)
router.get("/",                       response_model=SuccessResponse[list[VehiculoResponse]])(controller_vehiculo.listar_vehiculos)
router.get("/{id_vehiculo}",          response_model=SuccessResponse[VehiculoResponse])(controller_vehiculo.obtener_vehiculo)
router.patch("/{id_vehiculo}",        response_model=SuccessResponse[VehiculoResponse])(controller_vehiculo.actualizar_vehiculo)
router.patch("/{id_vehiculo}/estado", response_model=SuccessResponse[VehiculoResponse])(controller_vehiculo.cambiar_estado_vehiculo)
router.delete("/{id_vehiculo}",       response_model=SuccessResponse[dict[str, int]])(controller_vehiculo.eliminar_vehiculo)