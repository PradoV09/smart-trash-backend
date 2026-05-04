import asyncio
from database import SessionLocal
from sqlalchemy import select
from models.model_asignacionrutas import AsignacionRutas, EstadoAsignacion
from models.model_vehiculo import Vehiculo
from models.model_tripulacion import Tripulacion

async def main():
    async with SessionLocal() as session:
        result = await session.execute(
            select(AsignacionRutas).where(
                AsignacionRutas.estado == EstadoAsignacion.en_curso
            )
        )
        asignaciones = result.scalars().all()
        print(f"Found {len(asignaciones)} assignments en_curso")
        for a in asignaciones:
            print(f"ID: {a.id_asignacion}, Estado: {a.estado}")

if __name__ == "__main__":
    asyncio.run(main())
