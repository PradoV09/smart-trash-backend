# controllers/controller_vehiculo.py

"""Controladores del módulo de vehículos.

Estos handlers exponen el CRUD administrativo de camiones y delegan todas las
validaciones de negocio al `VehiculoService`.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from models.model_vehiculo import EstadoVehiculo
from models.model_usuarios import Usuario
from services.service_vehiculo import VehiculoService


async def crear_vehiculo(
    data: VehiculoCreate = Depends(VehiculoCreate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[VehiculoResponse]:
    """Crea un nuevo vehículo con placa única y estado inicial controlado."""
    vehiculo = await VehiculoService(db).añadir_vehiculo(data)
    return success_response(data=vehiculo, message="Vehículo creado exitosamente.")


async def listar_vehiculos(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[VehiculoResponse]]:
    """Recupera el listado completo de vehículos registrados."""
    vehiculos = await VehiculoService(db).obtener_todos_vehiculos()
    return success_response(data=vehiculos, message="Vehículos obtenidos exitosamente.")


async def obtener_vehiculo(
    id_vehiculo: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[VehiculoResponse]:
    """Devuelve la información puntual de un vehículo por id."""
    vehiculo = await VehiculoService(db).obtener_vehiculo_por_id(id_vehiculo)
    return success_response(data=vehiculo, message="Vehículo obtenido exitosamente.")


async def actualizar_vehiculo(
    id_vehiculo: int,
    data: VehiculoUpdate = Depends(VehiculoUpdate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[VehiculoResponse]:
    """Actualiza los campos editables del vehículo sin reemplazar todo el registro."""
    vehiculo = await VehiculoService(db).actualizar_vehiculo_por_id(id_vehiculo, data)
    return success_response(data=vehiculo, message="Vehículo actualizado exitosamente.")


async def cambiar_estado_vehiculo(
    id_vehiculo: int,
    estado: EstadoVehiculo,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[VehiculoResponse]:
    """Cambia únicamente el estado operativo del vehículo."""
    vehiculo = await VehiculoService(db).cambiar_estado_vehiculo(id_vehiculo, estado)
    return success_response(data=vehiculo, message="Estado del vehículo actualizado exitosamente.")


async def eliminar_vehiculo(
    id_vehiculo: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[dict[str, int]]:
    """Elimina físicamente el vehículo de la base de datos."""
    await VehiculoService(db).eliminar_vehiculo(id_vehiculo)
    return success_response(data={"id_vehiculo": id_vehiculo}, message="Vehículo eliminado exitosamente.")