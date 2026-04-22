# controllers/controller_tripulacion.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from schemas.schema_tripulacion import TripulacionCreate, TripulacionResponse
from services.service_tripulacion import TripulacionService
from models.model_usuarios import Usuario

async def crear_tripulacion(
    data: TripulacionCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> TripulacionResponse:
    tripulacion = await TripulacionService(db).crear_tripulacion(data)
    return success_response(data=tripulacion, message="Tripulación creada exitosamente.")

async def listar_tripulaciones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[TripulacionResponse]:
    tripulaciones = await TripulacionService(db).obtener_todas()
    return success_response(data=tripulaciones, message="Tripulaciones obtenidas exitosamente.")
