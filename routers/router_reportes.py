# routers/router_reportes.py

from fastapi import APIRouter, status
from schemas.schema_reportes import ReporteCreate, ReporteResponse
from schemas.schema_responses import SuccessResponse
from controllers import controller_reportes

router = APIRouter(prefix="/admin/reportes", tags=["Admin: Reportes"])

router.get("",  response_model=SuccessResponse[list[ReporteResponse]])(controller_reportes.listar_reportes)
router.get("/{id_reporte}", response_model=SuccessResponse[ReporteResponse])(controller_reportes.obtener_reporte)
router.patch("/{id_reporte}/terminar", response_model=SuccessResponse[ReporteResponse])(controller_reportes.terminar_reporte)