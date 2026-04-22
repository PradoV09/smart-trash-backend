import asyncio
from sqlalchemy import text
from database import engine, Base
import models.model_usuarios
import models.model_roles
import models.model_perfiles
import models.model_vehiculo
import models.model_asignacionrutas
import models.model_asignaciontripulacion

async def fix_db():
    async with engine.begin() as conn:
        print("Eliminando tabla tripulacion_asignacion para recrearla con el esquema correcto...")
        await conn.execute(text("DROP TABLE IF EXISTS tripulacion_asignacion CASCADE"))
        print("Recreando tablas...")
        await conn.run_sync(Base.metadata.create_all)
        print("¡Listo!")

if __name__ == "__main__":
    asyncio.run(fix_db())
