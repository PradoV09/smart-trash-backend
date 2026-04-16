# routers/router_reportes.py

from fastapi import APIRouter, status
from schemas.schema_reportes import ReporteCreate, ReporteResponse
from schemas.schema_responses import SuccessResponse
from controllers import controller_reportes

router = APIRouter(prefix="/admin/reportes", tags=["Admin: Reportes"])

router.post("/", response_model=SuccessResponse[ReporteResponse], status_code=status.HTTP_201_CREATED)(controller_reportes.crear_reporte)
router.get("/",  response_model=SuccessResponse[list[ReporteResponse]])(controller_reportes.listar_reportes)