# ⚙️ Configuración de Integración con API de Rutas

# Este archivo muestra cómo configurar la integración
# entre tu API de asignaciones y la API externa de rutas

# =====================================================
# VARIABLES DE ENTORNO (.env)
# =====================================================

# URL de tu API de rutas externa
# Cambia esta URL cuando despliegues a producción
# RUTAS_API_URL=http://localhost:8001

# Otras configuraciones de la aplicación
# DATABASE_URL=postgresql://user:password@localhost/smart_trash
# SECRET_KEY=tu_clave_secreta_muy_segura
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30

# =====================================================
# CONFIGURACIÓN POR ENTORNO
# =====================================================

# Desarrollo (development)
# RUTAS_API_URL=http://localhost:8001

# Staging
# RUTAS_API_URL=https://api-rutas-staging.tudominio.com

# Producción
# RUTAS_API_URL=https://api-rutas.tudominio.com

# =====================================================
# CONFIGURACIÓN EN CÓDIGO (settings.py)
# =====================================================

# En tu archivo core/settings.py, agrega:

# from pydantic import Field
# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     # ... otras configuraciones ...

#     # URL de la API externa de rutas
#     rutas_api_url: str = Field(
#         default="http://localhost:8001",
#         description="URL base de la API externa de rutas"
#     )

#     class Config:
#         env_file = ".env"
#         case_sensitive = False

# # Instancia global
# settings = Settings()

# =====================================================
# CONFIGURACIÓN DE CORS (si es necesario)
# =====================================================

# Si tu API de rutas está en un dominio diferente,
# configura CORS en main.py:

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend desarrollo
        "https://tu-frontend.com",  # Frontend producción
        "http://localhost:8001",  # Tu API de rutas
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# CONFIGURACIÓN DE LOGGING
# =====================================================

# Para debugging de la integración, agrega logging:

import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# En services/service_rutas_externo.py, usa logger en lugar de print:

logger = logging.getLogger(__name__)

# En lugar de print("Error...")
logger.error(f"Error conectando con API de rutas: {e}")

# =====================================================
# CONFIGURACIÓN DE TIMEOUTS
# =====================================================

# En services/service_rutas_externo.py:

# Timeout por defecto (10 segundos)
TIMEOUT_DEFAULT = 10.0

# Para APIs lentas, aumenta el timeout:
TIMEOUT_LENTO = 30.0

# En producción, considera timeouts más cortos:
TIMEOUT_PRODUCCION = 5.0

# =====================================================
# CONFIGURACIÓN DE AUTENTICACIÓN EXTERNA
# =====================================================

# Si tu API de rutas requiere autenticación:

# En .env
RUTAS_API_TOKEN=tu_token_para_api_rutas
RUTAS_API_KEY=tu_api_key_para_rutas

# En service_rutas_externo.py
class ServiceRutasExterno:
    def __init__(self):
        self.base_url = settings.rutas_api_url
        self.auth_token = settings.rutas_api_token
        self.api_key = settings.rutas_api_key

    async def _get_headers(self):
        """Headers para autenticación"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

# =====================================================
# CONFIGURACIÓN DE REINTENTOS
# =====================================================

# Para manejar fallos temporales de red:

import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class ServiceRutasExterno:
    @retry(
        stop=stop_after_attempt(3),  # Máximo 3 intentos
        wait=wait_exponential(multiplier=1, min=4, max=10)  # Espera exponencial
    )
    async def obtener_ruta_por_id(self, id_ruta: int):
        # Tu código aquí...
        pass

# =====================================================
# CONFIGURACIÓN DE HEALTH CHECKS
# =====================================================

# Para verificar que la API externa esté disponible:

async def health_check_rutas_api() -> bool:
    """Verifica que la API de rutas esté respondiendo"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.rutas_api_url}/health")
            return response.status_code == 200
    except:
        return False

# Endpoint de health check en tu API:
@app.get("/health")
async def health_check():
    rutas_ok = await health_check_rutas_api()
    return {
        "status": "ok" if rutas_ok else "degraded",
        "services": {
            "rutas_api": "ok" if rutas_ok else "error"
        }
    }

# =====================================================
# CONFIGURACIÓN DE RATE LIMITING
# =====================================================

# Si necesitas limitar las llamadas a la API externa:

# from slowapi import Limiter
# from slowapi.util import get_remote_address

# limiter = Limiter(key_func=get_remote_address)

# # En tus endpoints que llaman a la API externa:
# @app.post("/admin/asignaciones")
# @limiter.limit("10/minute")  # Máximo 10 llamadas por minuto
# async def crear_asignacion(...):
#     # Tu código...
#     pass

# =====================================================
# CONFIGURACIÓN DE CACHE (OPCIONAL)
# =====================================================

# Para mejorar rendimiento si las rutas no cambian frecuentemente:

# from cachetools import TTLCache
# import asyncio

# class ServiceRutasExterno:
#     def __init__(self):
#         self.cache = TTLCache(maxsize=100, ttl=300)  # 5 minutos TTL

#     async def obtener_ruta_por_id(self, id_ruta: int):
#         # Verificar cache primero
#         if id_ruta in self.cache:
#             return self.cache[id_ruta]

#         # Si no está en cache, hacer petición
#         ruta = await self._fetch_ruta_from_api(id_ruta)

#         # Guardar en cache
#         if ruta:
#             self.cache[id_ruta] = ruta

#         return ruta

# =====================================================
# EJEMPLOS DE CONFIGURACIÓN POR ENTORNO
# =====================================================

# .env.development
# RUTAS_API_URL=http://localhost:8001
# LOG_LEVEL=DEBUG
# TIMEOUT=10.0

# .env.staging
# RUTAS_API_URL=https://api-rutas-staging.tudominio.com
# LOG_LEVEL=INFO
# TIMEOUT=5.0

# .env.production
# RUTAS_API_URL=https://api-rutas.tudominio.com
# LOG_LEVEL=WARNING
# TIMEOUT=3.0

# =====================================================
# VERIFICACIÓN DE CONFIGURACIÓN
# =====================================================

# Script para verificar que todo esté configurado correctamente:

async def verificar_configuracion():
    """Verifica que la configuración sea correcta"""
    print("🔍 Verificando configuración...")

    # Verificar URL
    if not settings.rutas_api_url:
        print("❌ RUTAS_API_URL no configurada")
        return False

    # Verificar conectividad
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.rutas_api_url}/rutas/1")
            if response.status_code in [200, 404]:  # 404 es ok, significa que la API responde
                print("✅ API de rutas responde correctamente")
            else:
                print(f"⚠️ API de rutas responde con código {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando con API de rutas: {e}")
        return False

    print("✅ Configuración verificada correctamente")
    return True

# Ejecutar verificación:
# python -c "import asyncio; from config import verificar_configuracion; asyncio.run(verificar_configuracion())"