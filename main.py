# main.py

"""Punto de entrada principal de la API.

Este archivo:
1. crea la instancia de FastAPI,
2. configura CORS,
3. ejecuta tareas de arranque y cierre con lifespan,
4. monta todos los routers HTTP y WebSocket.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.error_handlers import register_exception_handlers
from core.response_builders import success_response
from core.settings import settings

from routers.router_auth import router as auth_router
from routers.router_usuarios import router as usuario_router
from routers.router_vehiculo import router as vehiculo_router
from routers.router_reportes import router as reporte_router
from routers.router_ws import router as ws_router
from routers.router_asignacionvehiculo import (
    router_admin      as asignacion_admin_router,
    router_driver     as asignacion_driver_router,
    router_recolector as asignacion_recolector_router,
    router_user       as asignacion_user_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación.

    Antes de aceptar tráfico:
    - importa y crea las tablas necesarias.

    Al finalizar:
    - deja un registro simple en consola para facilitar el monitoreo local.
    """
    from database import crear_tablas
    await crear_tablas()
    print("✅ Base de datos lista")
    yield
    print("🛑 Servidor detenido")


app = FastAPI(
    title="Smart Trash Route API",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,  # ✅ aquí va — evita 307 en tests y clientes
)

# Registra handlers globales para que todos los errores salgan con el mismo formato JSON.
register_exception_handlers(app)

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
app.include_router(ws_router)
app.include_router(asignacion_admin_router)
app.include_router(asignacion_driver_router)
app.include_router(asignacion_recolector_router)
app.include_router(asignacion_user_router)


@app.get("/")
def read_root():
    return success_response(
        data={"app": "Smart Trash Route API", "version": "1.0.0"},
        message="Bienvenido a la API Smart Trash Route!",
    )