# services/service_vehiculo.py

"""Servicios del módulo de vehículos.

Aquí se concentra la lógica del CRUD de camiones y el control de sus estados
operativos (`disponible`, `en_ruta`, `mantenimiento`, etc.).
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from models.model_vehiculo import Vehiculo, EstadoVehiculo
from schemas.schema_vehiculo import VehiculoCreate, VehiculoUpdate


class VehiculoService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def añadir_vehiculo(self, data: VehiculoCreate) -> Vehiculo:
        """Crea un vehículo nuevo verificando que la placa no esté repetida."""
        result = await self.db.execute(
            select(Vehiculo).where(Vehiculo.placa == data.placa)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un vehículo registrado con la placa '{data.placa}'.",
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
                detail=f"No se encontró un vehículo con id {id_vehiculo}.",
            )
        return vehiculo

    async def actualizar_vehiculo_por_id(self, id_vehiculo: int, data: VehiculoUpdate) -> Vehiculo:
        """Actualiza parcialmente los datos de un vehículo existente."""
        vehiculo = await self.obtener_vehiculo_por_id(id_vehiculo)
        for campo, valor in data.model_dump(exclude_none=True).items():
            setattr(vehiculo, campo, valor)
        await self.db.flush()
        return vehiculo

    async def cambiar_estado_vehiculo(self, id_vehiculo: int, estado: EstadoVehiculo) -> Vehiculo:
        """Actualiza únicamente el estado operativo del vehículo."""
        vehiculo = await self.obtener_vehiculo_por_id(id_vehiculo)
        vehiculo.estado = estado
        await self.db.flush()
        return vehiculo

    async def eliminar_vehiculo(self, id_vehiculo: int) -> None:
        vehiculo = await self.obtener_vehiculo_por_id(id_vehiculo)
        await self.db.delete(vehiculo)
        await self.db.flush()
