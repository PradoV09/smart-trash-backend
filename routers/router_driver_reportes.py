# routers/router_driver_reportes.py

from fastapi import APIRouter, status
from schemas.schema_reportes import ReporteDriverCreate, ReporteDriverResponse
from schemas.schema_responses import SuccessResponse
from controllers import controller_reportes

router = APIRouter(prefix="/driver/reportes", tags=["Driver: Reportes"])

router.post("", response_model=SuccessResponse[ReporteDriverResponse], status_code=status.HTTP_201_CREATED)(controller_reportes.crear_reporte_driver)
router.get("", response_model=SuccessResponse[list[ReporteDriverResponse]])(controller_reportes.listar_reportes_driver)
router.get("/{id_reporte}", response_model=SuccessResponse[ReporteDriverResponse])(controller_reportes.obtener_reporte_driver)
