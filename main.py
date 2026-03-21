from fastapi import FastAPI
from contextlib import asynccontextmanager
from config.connection import Base, engine
from controllers.controller_users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
    yield

app = FastAPI(title="Smart Trash Backend ", lifespan=lifespan)

app.include_router(users_router)