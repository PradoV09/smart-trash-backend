import asyncio
import logging
import sys
import os

# Asegurar que el directorio raíz está en el PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import SessionLocal
from models.model_vehiculo import Vehiculo, EstadoVehiculo
from schemas.schema_vehiculo import VehiculoCreate
from services.service_vehiculo import VehiculoService

logger = logging.getLogger(__name__)

VEHICULOS_A_CREAR = [
    {"placa": "IPY428", "modelo": "Default", "capacidad_m3": 10.0, "estado": EstadoVehiculo.disponible},
    {"placa": "IPY429", "modelo": "Default", "capacidad_m3": 10.0, "estado": EstadoVehiculo.disponible},
    {"placa": "IPY430", "modelo": "Default", "capacidad_m3": 10.0, "estado": EstadoVehiculo.disponible},
]

async def seed_vehiculos():
    async with SessionLocal() as db:
        service = VehiculoService(db)
        
        for v_data in VEHICULOS_A_CREAR:
            placa = v_data["placa"]
            # Verificar si existe localmente
            result = await db.execute(select(Vehiculo).where(Vehiculo.placa == placa))
            vehiculo = result.scalar_one_or_none()
            
            if vehiculo:
                logger.info(f"Vehículo {placa} ya existe en la BD local. Omitiendo.")
                continue
            
            logger.info(f"Creando vehículo {placa}...")
            create_schema = VehiculoCreate(**v_data)
            try:
                # añadir_vehiculo ya sincroniza con la API externa internamente
                await service.añadir_vehiculo(create_schema)
                await db.commit()
                logger.info(f"Vehículo {placa} creado y sincronizado exitosamente.")
            except Exception as e:
                await db.rollback()
                logger.error(f"Error al crear el vehículo {placa}: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_vehiculos())
