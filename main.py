# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.settings import settings

from routers.router_auth import router as auth_router
from routers.router_usuarios import router as usuario_router
from routers.router_vehiculo import router as vehiculo_router
from routers.router_reportes import router as reporte_router
from routers.router_asignacionvehiculo import (
    router_admin      as asignacion_admin_router,
    router_driver     as asignacion_driver_router,
    router_recolector as asignacion_recolector_router,
    router_user       as asignacion_user_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import crear_tablas
    await crear_tablas()
    print("✅ Base de datos lista")
    yield
    print("🛑 Servidor detenido")

app = FastAPI(
    title="Smart Trash Route API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(vehiculo_router)
app.include_router(reporte_router)
app.include_router(asignacion_admin_router)
app.include_router(asignacion_driver_router)
app.include_router(asignacion_recolector_router)
app.include_router(asignacion_user_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API Smart Trash Route!"}