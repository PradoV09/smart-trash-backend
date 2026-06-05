# controllers/controller_vehiculo.py

"""Controladores del módulo de vehículos.

Estos handlers exponen el CRUD administrativo de camiones y delegan todas las
validaciones de negocio al `VehiculoService`.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from models.model_vehiculo import EstadoVehiculo
from models.model_usuarios import Usuario
from services.service_vehiculo import VehiculoService
import logging

logger = logging.getLogger(__name__)

async def crear_vehiculo(
    data: VehiculoCreate = Depends(VehiculoCreate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[VehiculoResponse]:
    """Crea un nuevo vehículo con placa única y estado inicial controlado."""
    try:
        vehiculo = await VehiculoService(db).añadir_vehiculo(data)
        return success_response(data=vehiculo, message="Vehículo creado exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear vehículo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el vehículo: {str(e)}"
        )


async def listar_vehiculos(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[VehiculoResponse]]:
    """Recupera el listado completo de vehículos registrados."""
    try:
        vehiculos = await VehiculoService(db).obtener_todos_vehiculos()
        return success_response(data=vehiculos, message="Vehículos obtenidos exitosamente.")
    except Exception as e:
        logger.error(f"Error al listar vehículos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la lista de vehículos."
        )


async def obtener_vehiculo(
    id_vehiculo: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[VehiculoResponse]:
    """Devuelve la información puntual de un vehículo por id."""
    try:
        vehiculo = await VehiculoService(db).obtener_vehiculo_por_id(id_vehiculo)
        if not vehiculo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado.")
        return success_response(data=vehiculo, message="Vehículo obtenido exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener vehículo {id_vehiculo}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el vehículo."
        )


async def actualizar_vehiculo(
    id_vehiculo: int,
    data: VehiculoUpdate = Depends(VehiculoUpdate.as_form),
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[VehiculoResponse]:
    """Actualiza los campos editables del vehículo sin reemplazar todo el registro."""
    try:
        vehiculo = await VehiculoService(db).actualizar_vehiculo_por_id(id_vehiculo, data)
        if not vehiculo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado para actualizar.")
        return success_response(data=vehiculo, message="Vehículo actualizado exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar vehículo {id_vehiculo}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el vehículo: {str(e)}"
        )


async def cambiar_estado_vehiculo(
    id_vehiculo: int,
    estado: EstadoVehiculo,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[VehiculoResponse]:
    """Cambia únicamente el estado operativo del vehículo."""
    try:
        vehiculo = await VehiculoService(db).cambiar_estado_vehiculo(id_vehiculo, estado)
        if not vehiculo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado para cambiar estado.")
        return success_response(data=vehiculo, message="Estado del vehículo actualizado exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cambiar estado de vehículo {id_vehiculo}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el estado del vehículo."
        )


async def eliminar_vehiculo(
    id_vehiculo: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[dict[str, int]]:
    """Elimina físicamente el vehículo de la base de datos."""
    try:
        await VehiculoService(db).eliminar_vehiculo(id_vehiculo)
        return success_response(data={"id_vehiculo": id_vehiculo}, message="Vehículo eliminado exitosamente.")
    except Exception as e:
        logger.error(f"Error al eliminar vehículo {id_vehiculo}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el vehículo."
        )
