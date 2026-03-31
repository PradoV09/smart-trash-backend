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
from schemas.schema_asignaciovehiculo import (
    AsignacionCreate,
    AsignacionResponse,
    AsignacionPublicResponse,
)
from schemas.schema_tripulacionasignada import TripulacionCreate, TripulacionResponse
from services.service_asignaciovehiculo import AsignacionService
from services.service_tripulacionasignada import TripulacionService
from models.model_usuarios import Usuario
from fastapi import HTTPException, status

# --- Admin ---
async def crear_asignacion(
    data: AsignacionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Crea una nueva asignación de vehículo para una ruta externa."""
    return await AsignacionService(db).crear_asignacion(data)


async def listar_asignaciones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[AsignacionResponse]:
    """Lista todas las asignaciones con vehículo y tripulación asociada."""
    return await AsignacionService(db).obtener_asignaciones()


async def obtener_asignacion_admin(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Obtiene el detalle de una asignación desde el contexto administrativo."""
    return await AsignacionService(db).obtener_asignacion_id(id_asignacion)


async def cancelar_asignacion(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Cancela una asignación y libera el vehículo asociado."""
    return await AsignacionService(db).cancelar_asignacion(id_asignacion)


async def agregar_miembro_tripulacion(
    id_asignacion: int,
    data: TripulacionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> TripulacionResponse:
    """Agrega un usuario a la tripulación de una asignación pendiente."""
    return await TripulacionService(db).agregar_miembro(id_asignacion, data)


async def eliminar_miembro_tripulacion(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> dict:
    """Elimina un integrante de la tripulación mientras la asignación siga pendiente."""
    await TripulacionService(db).eliminar_miembro_asignacion(id_asignacion, id_usuario)
    return {"message": "Miembro eliminado de la tripulación"}


# --- Driver ---
async def ver_asignacion_driver(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    """Permite al conductor consultar la asignación que debe operar."""
    return await AsignacionService(db).obtener_asignacion_id(id_asignacion)


async def iniciar_recorrido(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    """Marca el inicio del recorrido y dispara el evento WebSocket correspondiente."""
    return await AsignacionService(db).iniciar_recorrido(id_asignacion)


async def finalizar_recorrido(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    """Cierra operativamente una asignación en curso."""
    return await AsignacionService(db).finalizar_recorrido(id_asignacion)


# --- Recolector ---
async def ver_asignacion_recolector(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> AsignacionResponse:
    """Permite al recolector consultar los datos de su asignación."""
    return await AsignacionService(db).obtener_asignacion_id(id_asignacion)


async def confirmar_participacion(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> TripulacionResponse:
    """Confirma la participación del integrante y deja trazabilidad en tiempo real."""
    return await TripulacionService(db).confirmar_asignacion(id_asignacion, id_usuario)


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
    return asignacion


async def verificar_asignacion_usuario(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = UserDep,
) -> AsignacionPublicResponse:
    """Expone una consulta puntual de asignación desde el contexto del usuario final."""
    return await AsignacionService(db).obtener_asignacion_id(id_asignacion)


async def verificar_asignacion_pendiente(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    """Valida que una asignación siga pendiente antes de cambiar su tripulación."""
    return await AsignacionService(db).verificar_asignacion_pendiente(id_asignacion)
