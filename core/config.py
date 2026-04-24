"""Configuración para integración con API externa.

Lee variables desde `.env` usando `python-dotenv`.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.settings import settings


@dataclass(frozen=True)
class ExternalAPIConfig:
    api_base_url: str
    perfil_id: str


def _es_url_base_local(url: str) -> bool:
    u = url.lower().removeprefix("https://").removeprefix("http://").split("/")[0]
    return (
        u.startswith("localhost")
        or u.startswith("127.")
        or u.startswith("0.0.0.0")
        or u.startswith("[::1]")
    )


def _resolver_url_base_api_externa() -> str:
    """URL para POST/GET /api/rutas, /api/vehiculos, /api/recorridos/…

    Orden:
    1. `INTEGRACION_API_URL` si está definida (control explícito).
    2. Si `RUTAS_API_URL` es localhost y `API` es una URL no local, usar `API`
       (evita enviar vehículos a :8001 apagado cuando ya tienes API en producción).
    3. Si no: `RUTAS_API_URL` o `API` (comportamiento clásico: backend de rutas primero).
    """
    expl = settings.INTEGRACION_API_URL.strip().rstrip("/")
    if expl:
        return expl
    rutas = settings.RUTAS_API_URL.strip().rstrip("/")
    api = settings.API.strip().rstrip("/")
    if rutas and _es_url_base_local(rutas) and api and not _es_url_base_local(api):
        return api
    return rutas or api


def get_external_api_config() -> ExternalAPIConfig:
    """Retorna la configuración de API externa (misma fuente que `Settings` / `.env`)."""
    api_base_url = _resolver_url_base_api_externa()
    perfil_id = settings.PERFIL_ID.strip()
    return ExternalAPIConfig(api_base_url=api_base_url, perfil_id=perfil_id)


@dataclass(frozen=True)
class AppConfig:
    """Configuración general de la aplicación."""
    upload_dir: str = "uploads/fotos"


def get_app_config() -> AppConfig:
    """Retorna la configuración general de la aplicación."""
    return AppConfig()
