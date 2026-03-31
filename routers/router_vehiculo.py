# routers/router_vehiculo.py

from fastapi import APIRouter, status
from schemas.schema_vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from models.model_vehiculo import EstadoVehiculo
from controllers import controller_vehiculo

router = APIRouter(prefix="/admin/vehiculos", tags=["Vehículos"])

router.post("/",                      response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED)(controller_vehiculo.crear_vehiculo)
router.get("/",                       response_model=list[VehiculoResponse])(controller_vehiculo.listar_vehiculos)
router.get("/{id_vehiculo}",          response_model=VehiculoResponse)(controller_vehiculo.obtener_vehiculo)
router.patch("/{id_vehiculo}",        response_model=VehiculoResponse)(controller_vehiculo.actualizar_vehiculo)
router.patch("/{id_vehiculo}/estado", response_model=VehiculoResponse)(controller_vehiculo.cambiar_estado_vehiculo)
router.delete("/{id_vehiculo}")(controller_vehiculo.eliminar_vehiculo)