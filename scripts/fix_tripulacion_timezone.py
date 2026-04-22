import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from sqlalchemy import text
from database import engine

async def migrate():
    async with engine.begin() as conn:
        print("Cambiando tripulaciones.created_at a TIMESTAMP WITH TIME ZONE...")
        await conn.execute(text("ALTER TABLE tripulaciones ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'UTC'"))
        
        print("Cambiando tripulacion_miembros.confirmado_at a TIMESTAMP WITH TIME ZONE (si no lo está)...")
        await conn.execute(text("ALTER TABLE tripulacion_miembros ALTER COLUMN confirmado_at TYPE TIMESTAMP WITH TIME ZONE USING confirmado_at AT TIME ZONE 'UTC'"))
        
        print("¡Migración completada!")

if __name__ == "__main__":
    asyncio.run(migrate())
