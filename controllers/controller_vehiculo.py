# controllers/vehiculo_controller.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from schemas.schema_vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from models.model_vehiculo import EstadoVehiculo
from models.model_usuarios import Usuario
from services.service_vehiculo import VehiculoService

async def crear_vehiculo(
    data: VehiculoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> VehiculoResponse:
    return await VehiculoService(db).añadir_vehiculo(data)

async def listar_vehiculos(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[VehiculoResponse]:
    return await VehiculoService(db).obtener_todos_vehiculos()

async def obtener_vehiculo(
    id_vehiculo: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> VehiculoResponse:
    return await VehiculoService(db).obtener_vehiculo_por_id(id_vehiculo)

async def actualizar_vehiculo(
    id_vehiculo: int,
    data: VehiculoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> VehiculoResponse:
    return await VehiculoService(db).actualizar_vehiculo_by_id(id_vehiculo, data)

async def cambiar_estado_vehiculo(
    id_vehiculo: int,
    estado: EstadoVehiculo,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> VehiculoResponse:
    return await VehiculoService(db).cambiar_estado_vehiculo(id_vehiculo, estado)

async def eliminar_vehiculo(
    id_vehiculo: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> dict:
    await VehiculoService(db).eliminar_vehiculo(id_vehiculo)
    return {"message": "Vehículo eliminado"}