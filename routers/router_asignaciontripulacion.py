# routers/router_asignaciontripulacion.py

"""Router para gestión de tripulación asignada.

Organiza endpoints por roles:
- Admin: gestión completa de tripulación
- Driver: consulta y confirmación de tripulación

Nota: El rol recolector no tiene endpoints en el MVP.
Solo existe como entidad para ser asignado a la tripulación por el admin.
El conductor es el único que confirma participación en el MVP.
"""

from fastapi import APIRouter, status
from schemas.schema_asignaciontripulacion import TripulacionCreate, TripulacionResponse
from schemas.schema_responses import SuccessResponse
from controllers import controller_asignaciontripulacion

# Admin
router_admin = APIRouter(prefix="/admin/asignaciones", tags=["Admin: Tripulación"])

router_admin.post("/{id_asignacion:int}/tripulacion", response_model=SuccessResponse[TripulacionResponse], status_code=status.HTTP_201_CREATED)(controller_asignaciontripulacion.agregar_miembro_tripulacion)
router_admin.delete("/{id_asignacion:int}/tripulacion/{id_usuario:int}", response_model=SuccessResponse[dict])(controller_asignaciontripulacion.eliminar_miembro_tripulacion)
router_admin.get("/{id_asignacion:int}/tripulacion", response_model=SuccessResponse[list[TripulacionResponse]])(controller_asignaciontripulacion.listar_tripulacion_asignacion)
router_admin.get("/todas", response_model=SuccessResponse[list[TripulacionResponse]])(controller_asignaciontripulacion.listar_todas_tripulaciones)

# Driver
router_driver = APIRouter(prefix="/driver/asignaciones", tags=["Driver: Tripulación"])

router_driver.get("/{id_asignacion:int}/tripulacion", response_model=SuccessResponse[list[TripulacionResponse]])(controller_asignaciontripulacion.ver_tripulacion_driver)
router_driver.post("/{id_asignacion:int}/confirmar", response_model=SuccessResponse[TripulacionResponse])(controller_asignaciontripulacion.confirmar_participacion_driver)
