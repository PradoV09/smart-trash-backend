import os
from dotenv import load_dotenv
import asyncpg
import asyncio

load_dotenv()

async def add_uuid_column():
    conn = await asyncpg.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    try:
        # Check if column exists
        result = await conn.fetchval("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'recorrido_posiciones' AND column_name = 'uuid'
        """)
        
        if result:
            print('La columna uuid ya existe')
        else:
            # Add column
            await conn.execute('ALTER TABLE recorrido_posiciones ADD COLUMN uuid VARCHAR(36)')
            print('Columna uuid agregada')
            
            # Generate UUIDs for existing rows
            await conn.execute('UPDATE recorrido_posiciones SET uuid = gen_random_uuid()::text WHERE uuid IS NULL')
            print('UUIDs generados para registros existentes')
            
            # Make NOT NULL
            await conn.execute('ALTER TABLE recorrido_posiciones ALTER COLUMN uuid SET NOT NULL')
            print('Columna uuid establecida como NOT NULL')
            
            # Add unique constraint
            await conn.execute('ALTER TABLE recorrido_posiciones ADD CONSTRAINT uq_recorrido_posiciones_uuid UNIQUE (uuid)')
            print('Restricción UNIQUE agregada')
            
            print('✅ Migración completada exitosamente')
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        await conn.close()

asyncio.run(add_uuid_column())
