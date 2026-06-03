"""Router para integración de recorridos con API externa."""

from uuid import UUID
from fastapi import APIRouter, Query, status

from controllers import controller_recorridos
from schemas.schema_recorridos_externos import (
    IniciarRecorridoRequest,
    PosicionesRecorridoResponse,
    RecorridoResponse,
    RegistrarPosicionRequest,
)
from schemas.schema_responses import SuccessResponse


router = APIRouter(prefix="/recorridos", tags=["Integración: Recorridos Externos"])

router.post(
    "/iniciar",
    response_model=SuccessResponse[RecorridoResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar recorrido externo",
    description="Inicia un recorrido en la API externa a partir de una ruta y un vehiculo.",
    response_description="Recorrido iniciado correctamente.",
    responses={
        403: {"description": "Accion no autorizada."},
        404: {"description": "Ruta o vehiculo no encontrado."},
        422: {"description": "Validacion fallida en los parametros enviados."},
        502: {"description": "No se pudo conectar con la API externa."},
    },
)(controller_recorridos.iniciar_recorrido)

router.post(
    "/{recorrido_id}/posiciones",
    response_model=SuccessResponse[RecorridoResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar posicion de recorrido",
    description=(
        "Registra una coordenada GPS en un recorrido activo. "
        "Acepta `lat`, `lon` y `perfil_id` (todos requeridos). "
        "Solo usuarios con rol `driver` pueden consumir este endpoint."
    ),
    response_description="Posicion registrada correctamente.",
    responses={
        403: {"description": "Accion no autorizada."},
        422: {"description": "Validacion fallida en body o path."},
        502: {"description": "No se pudo conectar con la API externa."},
    },
)(controller_recorridos.registrar_posicion)


@router.get(
    "/{recorrido_id}/posiciones",
    response_model=SuccessResponse[
        list[PosicionesRecorridoResponse] | PosicionesRecorridoResponse
    ],
    status_code=status.HTTP_200_OK,
    summary="Listar posiciones de un recorrido",
    description=(
        "Consulta el historial de posiciones GPS de un recorrido en la API externa. "
        "Es publico (no requiere autenticacion) y tambien puede ser consumido por administradores. "
        "El `perfil_id` puede enviarse por query o tomarse desde la configuracion del backend."
    ),
    response_description="Listado de posiciones del recorrido.",
    responses={
        403: {"description": "Accion no autorizada."},
        404: {"description": "Recorrido no encontrado."},
        422: {"description": "Validacion fallida en parametros."},
        502: {"description": "No se pudo conectar con la API externa."},
    },
)
async def listar_posiciones_recorrido(
    recorrido_id: UUID,
    perfil_id: str | None = Query(
        default=None,
        description="UUID del perfil propietario para validacion de permisos.",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    ),
):
    return await controller_recorridos.listar_posiciones(recorrido_id, perfil_id)
