import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from schemas.schema_vehiculo import VehiculoCreate
from services.service_vehiculo import VehiculoService
from core.settings import settings

async def main():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        service = VehiculoService(session)
        # Random placa to avoid conflict
        data = VehiculoCreate(
            placa="ZZZ124",
            marca="TestMarca",
            modelo="TestModelo",
            capacidad_m3=10.0,
            estado="disponible"
        )
        try:
            print("Creando vehiculo ZZ1...")
            v = await service.añadir_vehiculo(data)
            await session.commit()
            print("Vehiculo creado exitosamente localmente:", v.id_vehiculo, v.id_externo)
        except Exception as e:
            import traceback
            print("Error:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
