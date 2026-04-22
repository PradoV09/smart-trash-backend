# services/service_tripulacion.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from models.model_tripulacion import Tripulacion, TripulacionMiembro
from models.model_usuarios import Usuario
from schemas.schema_tripulacion import TripulacionCreate, TripulacionResponse

class TripulacionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_tripulacion(self, data: TripulacionCreate) -> Tripulacion:
        # Validar regla: 1 conductor + 3 recolectores
        conductores = [m for m in data.miembros if m.rol_tripulacion == "conductor"]
        recolectores = [m for m in data.miembros if m.rol_tripulacion == "recolector"]

        if len(conductores) != 1:
            raise HTTPException(status_code=400, detail="Una tripulación debe tener exactamente 1 conductor.")
        if len(recolectores) != 3:
            raise HTTPException(status_code=400, detail="Una tripulación debe tener exactamente 3 recolectores.")

        nueva_trip = Tripulacion(nombre=data.nombre)
        self.db.add(nueva_trip)
        await self.db.flush()

        for m in data.miembros:
            miembro = TripulacionMiembro(
                id_tripulacion=nueva_trip.id_tripulacion,
                id_usuario=m.id_usuario,
                rol_tripulacion=m.rol_tripulacion
            )
            self.db.add(miembro)
        
        await self.db.commit()
        
        # Devolver con relaciones cargadas
        result = await self.db.execute(
            select(Tripulacion)
            .options(
                selectinload(Tripulacion.miembros).selectinload(TripulacionMiembro.usuario).selectinload(Usuario.perfil),
                selectinload(Tripulacion.miembros).selectinload(TripulacionMiembro.usuario).selectinload(Usuario.rol)
            )
            .where(Tripulacion.id_tripulacion == nueva_trip.id_tripulacion)
        )
        return result.scalar_one()

    async def obtener_todas(self) -> list[Tripulacion]:
        result = await self.db.execute(
            select(Tripulacion).options(
                selectinload(Tripulacion.miembros).selectinload(TripulacionMiembro.usuario).selectinload(Usuario.perfil),
                selectinload(Tripulacion.miembros).selectinload(TripulacionMiembro.usuario).selectinload(Usuario.rol)
            )
        )
        return result.scalars().all()
