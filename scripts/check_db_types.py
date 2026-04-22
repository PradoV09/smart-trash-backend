import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from sqlalchemy import text
from database import engine

async def check_types():
    async with engine.connect() as conn:
        for table in ["tripulaciones", "tripulacion_miembros"]:
            print(f"\nTipos en tabla: {table}")
            res = await conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'"))
            for row in res:
                print(f"  {row[0]}: {row[1]}")

if __name__ == "__main__":
    asyncio.run(check_types())
