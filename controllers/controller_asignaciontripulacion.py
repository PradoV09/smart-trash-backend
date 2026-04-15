# controllers/controller_asignaciontripulacion.py

"""Controladores del módulo de tripulación asignada.

Este archivo organiza los endpoints por perfil de acceso:
- admin,
- driver,
- recolector.

Los controllers solo coordinan dependencias, permisos y respuestas.
La lógica de operación de tripulación vive en los services.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep, DriverDep, RecolectorDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_asignaciontripulacion import TripulacionCreate, TripulacionResponse
from services.service_asignaciontripulacion import TripulacionService
from models.model_usuarios import Usuario


# --- Admin ---
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
) -> SuccessResponse[dict]:
    """Elimina un integrante de la tripulación mientras la asignación siga pendiente."""
    await TripulacionService(db).eliminar_miembro_asignacion(id_asignacion, id_usuario)
    return success_response(
        data={"id_asignacion": id_asignacion, "id_usuario": id_usuario},
        message="Miembro eliminado de la tripulación exitosamente.",
    )


async def listar_tripulacion_asignacion(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[TripulacionResponse]]:
    """Lista todos los miembros de la tripulación de una asignación."""
    tripulacion = await TripulacionService(db).obtener_tripulacion_asignacion(id_asignacion)
    return success_response(data=tripulacion, message="Tripulación obtenida exitosamente.")


# --- Driver ---
async def ver_tripulacion_driver(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = DriverDep,
) -> SuccessResponse[list[TripulacionResponse]]:
    """Permite al conductor consultar la tripulación asignada a su recorrido."""
    tripulacion = await TripulacionService(db).obtener_tripulacion_asignacion(id_asignacion)
    return success_response(data=tripulacion, message="Tripulación obtenida exitosamente.")


async def confirmar_participacion_driver(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = DriverDep,
) -> TripulacionResponse:
    """El conductor confirma su participación en la asignación."""
    miembro = await TripulacionService(db).confirmar_asignacion(id_asignacion, usuario.id_usuario)
    return success_response(data=miembro, message="Participación confirmada exitosamente.")


# --- Recolector ---
async def confirmar_participacion_recolector(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> TripulacionResponse:
    """Confirma la participación del recolector y deja trazabilidad en tiempo real."""
    miembro = await TripulacionService(db).confirmar_asignacion(id_asignacion, id_usuario)
    return success_response(data=miembro, message="Participación confirmada exitosamente.")


async def ver_asignacion_recolector_tripulacion(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> TripulacionResponse:
    """Permite al recolector ver sus datos de tripulación en una asignación."""
    miembro = await TripulacionService(db).obtener_miembro_tripulacion(id_asignacion, id_usuario)
    return success_response(data=miembro, message="Datos de tripulación obtenidos exitosamente.")
