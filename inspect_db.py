import asyncio
from sqlalchemy import text
from database import SessionLocal

async def inspect_table():
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'tripulacion_asignacion'"))
        columns = result.scalars().all()
        print(f"Columns in tripulacion_asignacion: {columns}")

if __name__ == "__main__":
    asyncio.run(inspect_table())
