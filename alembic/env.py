from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from database import Base
from core.settings import settings

# importa todos tus modelos
from models.model_roles import Rol
from models.model_perfiles import Perfil
from models.model_usuarios import Usuario
from models.model_reportes import ReporteActividad
from models.model_vehiculo import Vehiculo
from models.model_asignacionvehiculo import AsignacionVehiculo
from models.model_tripulacionasignacion import TripulacionAsignacion

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    connectable = create_engine(url, future=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()