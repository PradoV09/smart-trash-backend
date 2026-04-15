# controllers/controller_asignaciovehiculo.py

"""Controladores del módulo de asignaciones y tripulación.

Este archivo organiza los endpoints por perfil de acceso:
- admin,
- driver,
- recolector,
- ciudadano.

Los controllers solo coordinan dependencias, permisos y respuestas.
La lógica de operación de rutas vive en los services.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep, DriverDep, RecolectorDep, UserDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_asignacionrutas import (
    AsignacionCreate,
    AsignacionResponse,
    AsignacionPublicResponse,
)
from schemas.schema_asignaciontripulacion import TripulacionCreate, TripulacionResponse
from services.service_asignacionrutas import AsignacionService
from services.service_asignaciontripulacion import TripulacionService
from models.model_usuarios import Usuario
from fastapi import HTTPException, status

# --- Admin ---
async def crear_asignacion(
    data: AsignacionCreate = Depends(AsignacionCreate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Crea una nueva asignación de vehículo para una ruta externa."""
    asignacion = await AsignacionService(db).crear_asignacion(data)
    return success_response(data=asignacion, message="Asignación creada exitosamente.")


async def listar_asignaciones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[AsignacionResponse]]:
    """Lista todas las asignaciones con vehículo y tripulación asociada."""
    asignaciones = await AsignacionService(db).obtener_asignaciones()
    return success_response(data=asignaciones, message="Asignaciones obtenidas exitosamente.")


async def obtener_detalles_ruta(
    id_ruta: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[dict]:
    """Obtiene los detalles completos de una ruta desde el servicio externo de rutas."""
    detalles = await AsignacionService(db).obtener_detalles_ruta(id_ruta)
    if not detalles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron detalles para la ruta con id {id_ruta}.",
        )
    return success_response(data=detalles, message="Detalles de ruta obtenidos exitosamente.")


async def obtener_asignacion_admin(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Obtiene el detalle de una asignación desde el contexto administrativo."""
    asignacion = await AsignacionService(db).obtener_asignacion_id(id_asignacion)
    return success_response(data=asignacion, message="Asignación obtenida exitosamente.")


async def cancelar_asignacion(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Cancela una asignación y libera el vehículo asociado."""
    asignacion = await AsignacionService(db).cancelar_asignacion(id_asignacion)
    return success_response(data=asignacion, message="Asignación cancelada exitosamente.")


async def agregar_miembro_tripulacion(
    id_asignacion: int,
    data: TripulacionCreate = Depends(TripulacionCreate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> TripulacionResponse:
    """Agrega un usuario a la tripulación de una asignación pendiente."""
    miembro = await TripulacionService(db).agregar_miembro(id_asignacion, data)
    return success_response(data=miembro, message="Miembro agregado a la tripulación exitosamente.")


async def eliminar_miembro_tripulacion(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> dict:
    """Elimina un integrante de la tripulación mientras la asignación siga pendiente."""
    await TripulacionService(db).eliminar_miembro_asignacion(id_asignacion, id_usuario)
    return success_response(
        data={"id_asignacion": id_asignacion, "id_usuario": id_usuario},
        message="Miembro eliminado de la tripulación exitosamente.",
    )


# --- Driver ---
async def ver_asignacion_driver(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    """Permite al conductor consultar la asignación que debe operar."""
    asignacion = await AsignacionService(db).obtener_asignacion_id(id_asignacion)
    return success_response(data=asignacion, message="Asignación del conductor obtenida exitosamente.")


async def iniciar_recorrido(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    """Marca el inicio del recorrido y dispara el evento WebSocket correspondiente."""
    asignacion = await AsignacionService(db).iniciar_recorrido(id_asignacion)
    return success_response(data=asignacion, message="Recorrido iniciado exitosamente.")


async def finalizar_recorrido(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    """Cierra operativamente una asignación en curso."""
    asignacion = await AsignacionService(db).finalizar_recorrido(id_asignacion)
    return success_response(data=asignacion, message="Recorrido finalizado exitosamente.")


# --- Recolector ---
async def ver_asignacion_recolector(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> AsignacionResponse:
    """Permite al recolector consultar los datos de su asignación."""
    asignacion = await AsignacionService(db).obtener_asignacion_id(id_asignacion)
    return success_response(data=asignacion, message="Asignación del recolector obtenida exitosamente.")


async def confirmar_participacion(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> TripulacionResponse:
    """Confirma la participación del integrante y deja trazabilidad en tiempo real."""
    miembro = await TripulacionService(db).confirmar_asignacion(id_asignacion, id_usuario)
    return success_response(data=miembro, message="Participación confirmada exitosamente.")


# --- User ciudadano ---
async def ver_horario_ruta(
    id_ruta: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = UserDep,
) -> AsignacionPublicResponse:
    """Consulta el horario disponible para una ruta externa específica."""
    asignacion = await AsignacionService(db).obtener_asignacion_ruta(id_ruta)
    if not asignacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró información de horario para la ruta externa '{id_ruta}'.",
        )
    return success_response(data=asignacion, message="Horario de ruta obtenido exitosamente.")


async def verificar_asignacion_usuario(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = UserDep,
) -> AsignacionPublicResponse:
    """Expone una consulta puntual de asignación desde el contexto del usuario final."""
    asignacion = await AsignacionService(db).obtener_asignacion_id(id_asignacion)
    return success_response(data=asignacion, message="Asignación del usuario obtenida exitosamente.")


async def verificar_asignacion_pendiente(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Valida que una asignación siga pendiente antes de cambiar su tripulación."""
    asignacion = await AsignacionService(db).verificar_asignacion_pendiente(id_asignacion)
    return success_response(data=asignacion, message="Asignación pendiente validada exitosamente.")
