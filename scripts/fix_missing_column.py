import sys
import os
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

import asyncio
from sqlalchemy import text
from database import engine

async def fix():
    async with engine.begin() as conn:
        print("Verificando si id_tripulacion existe en asignaciones_rutas...")
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'asignaciones_rutas' AND column_name = 'id_tripulacion'"))
        if not res.scalar():
            print("Agregando columna id_tripulacion a asignaciones_rutas...")
            # Primero nos aseguramos de que la tabla tripulaciones exista
            await conn.execute(text("CREATE TABLE IF NOT EXISTS tripulaciones (id_tripulacion SERIAL PRIMARY KEY, nombre VARCHAR(100), created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)"))
            
            # Agregamos la columna
            await conn.execute(text("ALTER TABLE asignaciones_rutas ADD COLUMN id_tripulacion INTEGER REFERENCES tripulaciones(id_tripulacion)"))
            print("Columna agregada exitosamente.")
        else:
            print("La columna id_tripulacion ya existe.")

        print("Verificando columnas en tripulacion_miembros...")
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'tripulacion_miembros'"))
        actual_cols = res.scalars().all()
        
        if "confirmado" not in actual_cols:
            print("Agregando columna confirmado a tripulacion_miembros...")
            await conn.execute(text("ALTER TABLE tripulacion_miembros ADD COLUMN confirmado BOOLEAN DEFAULT FALSE NOT NULL"))
        
        if "confirmado_at" not in actual_cols:
            print("Agregando columna confirmado_at a tripulacion_miembros...")
            await conn.execute(text("ALTER TABLE tripulacion_miembros ADD COLUMN confirmado_at TIMESTAMP WITH TIME ZONE"))
        
        print("¡Verificación y corrección completada!")

if __name__ == "__main__":
    asyncio.run(fix())
