import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from core.settings import settings

async def update_enum():
    # Creamos un motor temporal con AUTOCOMMIT
    engine_autocommit = create_async_engine(settings.DATABASE_URL, isolation_level="AUTOCOMMIT")
    async with engine_autocommit.connect() as conn:
        print("Intentando agregar 'conductor' al enum 'roltripulacion' (AUTOCOMMIT)...")
        try:
            await conn.execute(text("ALTER TYPE roltripulacion ADD VALUE 'conductor'"))
            print("Valor 'conductor' agregado exitosamente.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("El valor 'conductor' ya existe o hubo un conflicto menor.")
            else:
                print(f"Error al actualizar enum: {e}")
    await engine_autocommit.dispose()

if __name__ == "__main__":
    asyncio.run(update_enum())
