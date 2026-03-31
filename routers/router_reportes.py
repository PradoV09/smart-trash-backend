# routers/reporte_router.py

from fastapi import APIRouter
from schemas.schema_reportes import ReporteCreate, ReporteResponse
from controllers import controller_reportes

router = APIRouter(prefix="/admin/reportes", tags=["Reportes"])

router.post("/", response_model=ReporteResponse)(controller_reportes.crear_reporte)
router.get("/",  response_model=list[ReporteResponse])(controller_reportes.listar_reportes)