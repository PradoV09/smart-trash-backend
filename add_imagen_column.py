import os
from dotenv import load_dotenv
import asyncpg
import asyncio

load_dotenv()

async def add_imagen_column():
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
            WHERE table_name = 'recorrido_posiciones' AND column_name = 'imagen'
        """)
        
        if result:
            print('La columna imagen ya existe')
        else:
            # Add column
            await conn.execute('ALTER TABLE recorrido_posiciones ADD COLUMN imagen VARCHAR(255)')
            print('✅ Columna imagen agregada exitosamente')
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        await conn.close()

asyncio.run(add_imagen_column())
