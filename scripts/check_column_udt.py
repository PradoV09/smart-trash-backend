import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from sqlalchemy import text
from database import engine

async def check_column_type():
    async with engine.connect() as conn:
        print("Checking type name for 'rol_tripulacion' in 'tripulacion_miembros'...")
        res = await conn.execute(text("""
            SELECT udt_name 
            FROM information_schema.columns 
            WHERE table_name = 'tripulacion_miembros' AND column_name = 'rol_tripulacion'
        """))
        row = res.fetchone()
        if row:
            print(f"  UDT Name: {row[0]}")

if __name__ == "__main__":
    asyncio.run(check_column_type())
