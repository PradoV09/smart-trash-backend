"""Configuración central de la base de datos.

Aquí se define:
- el motor asíncrono de SQLAlchemy,
- la factoría de sesiones `AsyncSession`,
- la clase base para los modelos ORM,
- la rutina de creación de tablas al arrancar la app.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,  # ahora con +asyncpg
    echo=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base = declarative_base()

async def crear_tablas():
    """Carga todos los modelos y crea sus tablas si aún no existen.

    Esta función se ejecuta en el `lifespan` de FastAPI y garantiza
    que el esquema base esté disponible al iniciar en desarrollo.
    """
    import models.model_usuarios
    import models.model_roles
    import models.model_perfiles
    import models.model_reportes
    import models.model_vehiculo
    import models.model_tripulacion
    import models.model_asignacionrutas
    import models.model_auth
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)