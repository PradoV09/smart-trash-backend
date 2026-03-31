# services/vehiculo_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from models.model_vehiculo import Vehiculo, EstadoVehiculo
from schemas.schema_vehiculo import VehiculoCreate, VehiculoUpdate

class VehiculoService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def añadir_vehiculo(self, data: VehiculoCreate) -> Vehiculo:
        result = await self.db.execute(
            select(Vehiculo).where(Vehiculo.placa == data.placa)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un vehículo con esa placa",
            )
        vehiculo = Vehiculo(**data.model_dump())
        self.db.add(vehiculo)
        await self.db.flush()
        return vehiculo

    async def obtener_todos_vehiculos(self) -> list[Vehiculo]:
        result = await self.db.execute(select(Vehiculo))
        return result.scalars().all()

    async def obtener_vehiculo_por_id(self, id_vehiculo: int) -> Vehiculo:
        result = await self.db.execute(
            select(Vehiculo).where(Vehiculo.id_vehiculo == id_vehiculo)
        )
        vehiculo = result.scalar_one_or_none()
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehículo no encontrado",
            )
        return vehiculo

    async def update_vehiculo_por_id(self, id_vehiculo: int, data: VehiculoUpdate) -> Vehiculo:
        vehiculo = await self.obtener_vehiculo_por_id(id_vehiculo)
        for campo, valor in data.model_dump(exclude_none=True).items():
            setattr(vehiculo, campo, valor)
        await self.db.flush()
        return vehiculo

    async def cambiar_estado_vehiculo(self, id_vehiculo: int, estado: EstadoVehiculo) -> Vehiculo:
        vehiculo = await self.obtener_vehiculo_por_id(id_vehiculo)
        vehiculo.estado = estado
        await self.db.flush()
        return vehiculo

    async def eliminar_vehiculo(self, id_vehiculo: int) -> None:
        vehiculo = await self.obtener_vehiculo_por_id(id_vehiculo)
        await self.db.delete(vehiculo)
        await self.db.flush()
