import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from sqlalchemy import text
from database import engine

async def migrate_asignaciones_timezone():
    async with engine.begin() as conn:
        print("Migrando columnas de 'asignaciones_rutas' a TIMESTAMP WITH TIME ZONE...")
        
        # Alterar hora_salida
        await conn.execute(text("""
            ALTER TABLE asignaciones_rutas 
            ALTER COLUMN hora_salida TYPE TIMESTAMP WITH TIME ZONE 
            USING hora_salida AT TIME ZONE 'UTC'
        """))
        
        # Alterar fecha
        await conn.execute(text("""
            ALTER TABLE asignaciones_rutas 
            ALTER COLUMN fecha TYPE TIMESTAMP WITH TIME ZONE 
            USING fecha AT TIME ZONE 'UTC'
        """))
        
        # Alterar created_at
        await conn.execute(text("""
            ALTER TABLE asignaciones_rutas 
            ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE 
            USING created_at AT TIME ZONE 'UTC'
        """))
        
        print("Migración completada exitosamente.")

if __name__ == "__main__":
    asyncio.run(migrate_asignaciones_timezone())
