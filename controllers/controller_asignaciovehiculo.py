# controllers/asignacion_controller.py

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
    return await AsignacionService(db).crear(data)

async def listar_asignaciones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[AsignacionResponse]:
    return await AsignacionService(db).obtener_asignaciones()

async def obtener_asignacion_admin(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    return await AsignacionService(db).obtener_asignacion_id(id_asignacion)

async def cancelar_asignacion(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    return await AsignacionService(db).cancelar_asignacion(id_asignacion)

async def agregar_miembro_tripulacion(
    id_asignacion: int,
    data: TripulacionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> TripulacionResponse:
    return await TripulacionService(db).agregar_miembro(id_asignacion, data)

async def eliminar_miembro_tripulacion(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> dict:
    await TripulacionService(db).eliminar_miembro(id_asignacion, id_usuario)
    return {"message": "Miembro eliminado de la tripulación"}

# --- Driver ---
async def ver_asignacion_driver(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    return await AsignacionService(db).obtener_asignacion_id(id_asignacion)

async def iniciar_recorrido(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    return await AsignacionService(db).iniciar_recorrido(id_asignacion)

async def finalizar_recorrido(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = DriverDep,
) -> AsignacionResponse:
    return await AsignacionService(db).finalizar_recorrido(id_asignacion)

# --- Recolector ---
async def ver_asignacion_recolector(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> AsignacionResponse:
    return await AsignacionService(db).obtener_asignacion_id(id_asignacion)

async def confirmar_participacion(
    id_asignacion: int,
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = RecolectorDep,
) -> TripulacionResponse:
    return await TripulacionService(db).confirmar_asignacion(id_asignacion, id_usuario)

# --- User ciudadano ---
async def ver_horario_ruta(
    id_ruta: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = UserDep,
) -> AsignacionPublicResponse:
    asignacion = await AsignacionService(db).obtener_asignacion_ruta(id_ruta)
    if not asignacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruta no encontrada",
        )
    return asignacion

async def verificar_asignacion_usuario(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = UserDep,
) -> AsignacionPublicResponse:
    return await AsignacionService(db).obtener_asignacion_id(id_asignacion)


async def verificar_asignacion_pendiente(
    id_asignacion: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> AsignacionResponse:
    return await AsignacionService(db).verificar_asignacion_pendiente(id_asignacion)
