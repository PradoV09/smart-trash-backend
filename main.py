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

Autor: Heiner Jair Godoy Zamora
Versión: 1.0.0
"""

# ============================================================================
# IMPORTS - Librerías estándar
# ============================================================================

from contextlib import asynccontextmanager

# ============================================================================
# IMPORTS - Librerías de terceros
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from routers.router_ws import router as ws_router
from routers.router_asignacionrutas import (
    router_admin as asignacion_admin_router,
    router_driver as asignacion_driver_router,
    router_user as asignacion_user_router,
)
from routers.router_asignaciontripulacion import (
    router_admin as tripulacion_admin_router,
    router_driver as tripulacion_driver_router,
)

# ============================================================================
# CONFIGURACIÓN DE LIFESPAN - Ciclo de vida de la aplicación
# ============================================================================


async def inicializar_base_datos():
    """Crea las tablas de la base de datos si no existen."""
    from database import crear_tablas
    await crear_tablas()


async def precargar_configuraciones():
    """Pre-carga configuraciones críticas para reducir latencia inicial."""
    # Importar módulos que se usan frecuentemente para cache de import
    from core.security import pwd_context
    from core.websocket_manager import ws_manager

    # Verificar que las importaciones funcionen
    assert pwd_context is not None
    assert ws_manager is not None


async def verificar_conexion_db():
    """Verifica la conexión a la base de datos."""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
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
app.include_router(auth_router)

# 👥 Gestión de usuarios
app.include_router(usuario_router)

# 🚛 Gestión de vehículos
app.include_router(vehiculo_router)

# 📊 Reportes y estadísticas (Admin - gestión)
app.include_router(reporte_router)

# 📢 Reportes públicos (Ciudadanos - sin autenticación)
app.include_router(reporte_publico_router)

# 📡 WebSockets y tiempo real
app.include_router(
    ws_router,
    prefix="/ws",
    tags=["WebSockets"]
)

# 📋 Asignaciones de vehículos (diferentes roles)
app.include_router(asignacion_admin_router)
app.include_router(asignacion_driver_router)
app.include_router(asignacion_user_router)

# 👥 Tripulación de asignaciones (diferentes roles)
app.include_router(tripulacion_admin_router)
app.include_router(tripulacion_driver_router)

# ============================================================================
# ENDPOINTS PRINCIPALES - Endpoints de aplicación
# ============================================================================


@app.get(
    "/",
    summary="Información de la API",
    description="Retorna información básica sobre la API y su estado."
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
            "redoc": "/redoc"
        },
        message="Bienvenido a la API Smart Trash Route!",
    )


@app.get(
    "/health",
    summary="Health Check",
    description="Verifica el estado de salud de la aplicación y sus dependencias."
)
def health_check():
    """
    Health check básico para monitoreo y load balancers.

    Retorna el estado general de la aplicación.
    """
    return success_response(
        data={
            "status": "healthy",
            "timestamp": "2026-04-02T12:00:00Z",  # Se actualizaría dinámicamente
            "version": "1.0.0"
        },
        message="API funcionando correctamente",
    )

# ============================================================================
# INICIALIZACIÓN COMPLETADA
# ============================================================================

# El servidor se inicia automáticamente cuando se ejecuta este archivo
# con: uvicorn main:app --reload