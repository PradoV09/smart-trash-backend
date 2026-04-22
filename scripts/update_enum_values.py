import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from sqlalchemy import text
from database import engine

async def update_enum():
    # ALTER TYPE ADD VALUE no puede ejecutarse en una transacción
    async with engine.connect() as conn:
        print("Intentando agregar 'conductor' al enum 'roltripulacion'...")
        try:
            # En Postgres, ALTER TYPE ADD VALUE no se puede revertir, 
            # y asyncpg/sqlalchemy intentan manejar transacciones.
            # Usamos una conexión directa para intentar ejecutarlo fuera de un bloque BEGIN/COMMIT si es posible,
            # o simplemente lo intentamos.
            await conn.execute(text("ALTER TYPE roltripulacion ADD VALUE IF NOT EXISTS 'conductor'"))
            print("Valor 'conductor' asegurado en el enum.")
        except Exception as e:
            print(f"Error al actualizar enum: {e}")
            # Si IF NOT EXISTS no es soportado (depende de la versión de PG), 
            # es posible que falle si ya existe, pero ya verificamos que no.

if __name__ == "__main__":
    asyncio.run(update_enum())
