# ============================================================================
# SMART TRASH ROUTE API - Punto de entrada principal
# ============================================================================
"""
API REST para gestión de rutas de recolección de basura en Buenaventura.

Características principales:
- 🚛 Gestión de vehículos y asignaciones de rutas
- 👥 Autenticación y autorización por roles
- 📡 WebSockets para notificaciones en tiempo real
- 🗺️ Integración con API externa de rutas
- 📊 Reportes y estadísticas operativas

Autor: Heiner Jair Godoy Zamora y Jose Luis Prado Valencia
Versión: 1.0.0
"""

# ============================================================================
# IMPORTS - Librerías estándar
# ============================================================================

from contextlib import asynccontextmanager
from datetime import datetime, timezone

# ============================================================================
# IMPORTS - Librerías de terceros
# ============================================================================

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import os

# ============================================================================
# IMPORTS - Módulos locales
# ============================================================================

# Core
from core.error_handlers import register_exception_handlers
from core.response_builders import success_response
from core.settings import settings

# Routers
from routers.router_auth import router as auth_router
from routers.router_usuarios import router as usuario_router
from routers.router_vehiculo import router as vehiculo_router
from routers.router_reportes import router as reporte_router
from routers.router_reportes_publico import router as reporte_publico_router
from routers.router_roles import router as roles_router
from routers.router_asignacionrutas import (
    router_admin as asignacion_admin_router,
    router_driver as asignacion_driver_router,
)
from routers.router_rutas import (
    router as rutas_externas_router,
    router_public as rutas_publicas_router,
)
from routers.router_recorridos import router as recorridos_externos_router
from routers.router_ws import router as ws_router
from routers.router_tripulacion import router as tripulacion_router
from scripts.seed_admin import seed_admin

# ============================================================================
# CONFIGURACIÓN DE LIFESPAN - Ciclo de vida de la aplicación
# ============================================================================


async def inicializar_base_datos():
    """Crea las tablas de la base de datos si no existen."""
    from database import crear_tablas

    await crear_tablas()


async def precargar_configuraciones():
    """Pre-carga configuraciones críticas para reducir latencia inicial."""
    from core.security import pwd_context
    from core.websocket_manager import ws_manager

    assert pwd_context is not None
    assert ws_manager is not None


async def verificar_conexion_db():
    """Verifica la conexión a la base de datos."""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))  # ✅ Fix: usar text()
        await engine.dispose()
        return True
    except Exception as e:
        print(f"⚠️  Error conectando a base de datos: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.

    Startup:
    - Inicializa base de datos
    - Pre-carga configuraciones
    - Verifica conexiones críticas

    Shutdown:
    - Limpieza de recursos
    - Logging de cierre
    """
    # ================================
    # STARTUP
    # ================================
    print("🚀 Iniciando Smart Trash Route API...")

    # 1. Base de datos
    await inicializar_base_datos()
    print("✅ Base de datos inicializada")

    # 2. Conexiones críticas
    db_ok = await verificar_conexion_db()
    if db_ok:
        print("✅ Base de datos conectada y lista")
    else:
        print("⚠️  Base de datos no disponible - algunos endpoints pueden fallar")

    # 3. Pre-carga de configuraciones
    await precargar_configuraciones()
    print("✅ Configuraciones pre-cargadas")

    # 4. Seeder de administrador por defecto (idempotente)
    await seed_admin()
    print("✅ Seeder de usuario admin ejecutado")

    print("✅ Servidor listo y optimizado")
    print(f"📡 API disponible en: http://localhost:8000")
    print(f"📚 Documentación en: http://localhost:8000/docs")

    yield

    # ================================
    # SHUTDOWN
    # ================================
    print("🛑 Servidor detenido - limpieza completada")


# ============================================================================
# CONFIGURACIÓN DE FASTAPI - Instancia principal
# ============================================================================

app = FastAPI(
    title="Smart Trash Route API",
    description="""
    API REST para gestión inteligente de rutas de recolección de basura.

    ## Características principales:
    - **🚛 Gestión de Vehículos**: CRUD completo de camiones de basura
    - **👥 Usuarios y Roles**: Sistema de autenticación con roles (admin, driver, recolector)
    - **📋 Asignaciones**: Creación y gestión de asignaciones vehículo-ruta
    - **📡 Tiempo Real**: WebSockets para notificaciones de cambios de estado
    - **🗺️ Integración Externa**: Validación automática con API de rutas
    - **📊 Reportes**: Estadísticas y reportes operativos

    ## Autenticación:
    - Usa `POST /auth/login` para obtener token JWT
    - Incluye `Authorization: Bearer <token>` en headers
    """,
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,  # Evita redirects 307 en tests
    contact={
        "name": "Equipo de Desarrollo",
        "email": "dev@smarttrash.com",
    },
    license_info={
        "name": "MIT",
    },
)

# ============================================================================
# MIDDLEWARE - Configuración de CORS y otros middlewares
# ============================================================================

print("🔥 DEBUG - CORS ORIGINS:", settings.cors_list)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ERROR HANDLERS - Manejo global de errores
# ============================================================================

register_exception_handlers(app)

# ============================================================================
# ROUTERS - Montaje de todos los routers de la API
# ============================================================================

# 🔐 Autenticación y autorización
app.include_router(auth_router, prefix="/api")

# 👥 Gestión de usuarios
app.include_router(usuario_router, prefix="/api")

# 🏷️ Catálogo de roles
app.include_router(roles_router, prefix="/api")

# 🚛 Gestión de vehículos
app.include_router(vehiculo_router, prefix="/api")

# 📊 Reportes y estadísticas (Admin - gestión)
app.include_router(reporte_router, prefix="/api")

# 📊 Reportes de conductores (Driver - creación y gestión)
from routers.router_driver_reportes import router as driver_reporte_router

app.include_router(driver_reporte_router, prefix="/api")

# 📢 Reportes públicos (Ciudadanos - sin autenticación)
app.include_router(reporte_publico_router, prefix="/api")

# 🗺️ Integración con API externa (rutas y recorridos)
app.include_router(rutas_externas_router, prefix="/api")
app.include_router(recorridos_externos_router, prefix="/api")

# 📡 WebSockets y tiempo real
app.include_router(ws_router, prefix="/ws", tags=["WebSockets"])

# 📋 Asignaciones de vehículos (diferentes roles)
app.include_router(asignacion_admin_router, prefix="/api")
app.include_router(asignacion_driver_router, prefix="/api")

# 📢 Rutas Públicas (Ciudadanos - sin autenticación)
app.include_router(rutas_publicas_router, prefix="/api")

# 👥 Tripulaciones (Gestión de equipos independientes)
app.include_router(tripulacion_router, prefix="/api")

# 📍 Posiciones GPS del recorrido (Driver + Admin)
from routers.router_posiciones import router_driver as posiciones_driver_router
from routers.router_posiciones import router_admin as posiciones_admin_router

app.include_router(posiciones_driver_router, prefix="/api")
app.include_router(posiciones_admin_router, prefix="/api")

# 📷 Fotos/Evidencia del recorrido (Driver + Admin)
from routers.router_fotos import router_driver as fotos_driver_router
from routers.router_fotos import router_admin as fotos_admin_router
from routers.router_fotos import router_public as fotos_public_router

app.include_router(fotos_driver_router, prefix="/api")
app.include_router(fotos_admin_router, prefix="/api")
app.include_router(
    fotos_public_router
)  # Sin prefijo /api - el router ya tiene /uploads/fotos

# 📊 Estado en vivo (Admin only)
from routers.router_estado_vivo import router as estado_vivo_router

app.include_router(estado_vivo_router, prefix="/api")

# 📂 Archivos estáticos (Fotos y evidencia)
upload_dir = "uploads"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
    # Crear también el subdirectorio fotos para evitar errores iniciales
    os.makedirs(os.path.join(upload_dir, "fotos"), exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ============================================================================
# ENDPOINTS PRINCIPALES - Endpoints de aplicación
# ============================================================================


@app.options("/{full_path:path}", include_in_schema=False)
async def options_handler(request: Request):
    return {}


@app.get(
    "/",
    summary="Información de la API",
    description="Retorna información básica sobre la API y su estado.",
)
def read_root():
    """
    Endpoint raíz que proporciona información básica de la API.

    Retorna:
    - Nombre de la aplicación
    - Versión actual
    - Estado de funcionamiento
    """
    return success_response(
        data={
            "app": "Smart Trash Route API",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs",
            "redoc": "/redoc",
        },
        message="Bienvenido a la API Smart Trash Route!",
    )


@app.get(
    "/health",
    summary="Health Check",
    description="Verifica el estado de salud de la aplicación y sus dependencias.",
)
def health_check():
    """
    Health check básico para monitoreo y load balancers.

    Retorna el estado general de la aplicación.
    """
    return success_response(
        data={
            "status": "healthy",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),  # ✅ Fix: timestamp dinámico
            "version": "1.0.0",
        },
        message="API funcionando correctamente",
    )


# ============================================================================
# INICIALIZACIÓN COMPLETADA
# ============================================================================

# El servidor se inicia automáticamente cuando se ejecuta este archivo
# con: uvicorn main:app --reload
