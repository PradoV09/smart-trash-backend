# routers/router_reportes_publico.py

"""Router para reportes públicos de ciudadanos.

Permite a usuarios no autenticados reportar problemas de recolección de basura
sin necesidad de crear una cuenta o iniciar sesión.
"""

from fastapi import APIRouter, status
from schemas.schema_reportes_publico import ReportePublicoCreate, ReportePublicoResponse
from schemas.schema_responses import SuccessResponse
from controllers import controller_reportes_publico

router = APIRouter(prefix="/reportes", tags=["Público: Reportes"])

router.post(
    "",
    response_model=SuccessResponse[ReportePublicoResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Crear reporte público",
    description="Permite a ciudadanos reportar problemas de recolección sin autenticación"
)(controller_reportes_publico.crear_reporte_publico)
