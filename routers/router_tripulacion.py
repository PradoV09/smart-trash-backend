# routers/router_tripulacion.py

from fastapi import APIRouter
from controllers import controller_tripulacion as controller

router = APIRouter(prefix="/admin/tripulaciones", tags=["Tripulaciones"])

router.post("", response_model=None)(controller.crear_tripulacion)
router.get("", response_model=None)(controller.listar_tripulaciones)
