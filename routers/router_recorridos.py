"""Router para integración de recorridos con API externa."""

from fastapi import APIRouter, status

from controllers import controller_recorridos
from schemas.schema_recorridos_externos import (
    IniciarRecorridoRequest,
    RecorridoResponse,
    RegistrarPosicionRequest,
)
from schemas.schema_responses import SuccessResponse


router = APIRouter(prefix="/recorridos", tags=["Integración: Recorridos Externos"])

router.post(
    "/iniciar",
    response_model=SuccessResponse[RecorridoResponse],
    status_code=status.HTTP_201_CREATED,
)(controller_recorridos.iniciar_recorrido)

router.post(
    "/{recorrido_id}/posiciones",
    response_model=SuccessResponse[RecorridoResponse],
    status_code=status.HTTP_201_CREATED,
)(controller_recorridos.registrar_posicion)
