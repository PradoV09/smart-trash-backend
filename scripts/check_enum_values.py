import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from sqlalchemy import text
from database import engine

async def check_enum():
    async with engine.connect() as conn:
        print("Checking enum values for 'roltripulacion'...")
        res = await conn.execute(text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'roltripulacion'"))
        for row in res:
            print(f"  Value: {row[0]}")

if __name__ == "__main__":
    asyncio.run(check_enum())
