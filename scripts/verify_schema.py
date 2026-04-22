import sys
import os
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

import asyncio
from sqlalchemy import text
from database import engine

async def verify_schema():
    async with engine.connect() as conn:
        tables_to_check = {
            "asignaciones_rutas": ["id_asignacion", "id_vehiculo", "id_ruta", "id_tripulacion", "hora_salida", "fecha", "estado", "created_at"],
            "tripulaciones": ["id_tripulacion", "nombre", "created_at"],
            "tripulacion_miembros": ["id", "id_tripulacion", "id_usuario", "rol_tripulacion", "confirmado", "confirmado_at"]
        }
        
        for table, expected_cols in tables_to_check.items():
            print(f"Checking table: {table}")
            res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"))
            actual_cols = res.scalars().all()
            if not actual_cols:
                print(f"  [ERROR] Table '{table}' DOES NOT EXIST!")
                continue
            
            for col in expected_cols:
                if col in actual_cols:
                    print(f"  [OK] Column '{col}' exists.")
                else:
                    print(f"  [MISSING] Column '{col}' IS MISSING!")

if __name__ == "__main__":
    asyncio.run(verify_schema())
