# core/settings.py

from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Raíz del proyecto (no depender del cwd al lanzar uvicorn desde otra carpeta)
_ROOT = Path(__file__).resolve().parents[1]
_ENV_PATH = _ROOT / ".env"
load_dotenv(_ENV_PATH, override=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        # Si el SO/IDE exporta PERFIL_ID="" o API="", no pisar valores del .env
        env_ignore_empty=True,
    )

    DATABASE_URL:        str
    SECRET_KEY:          str
    JWT_SECRET:          str
    JWT_ALGORITHM:       str = "HS256"
    JWT_EXPIRE_MINUTES:  int = 480
    CORS_ORIGINS:        str = "http://localhost:4200"
    RUTAS_API_URL:       str = "http://localhost:8001"  # URL de la API externa de rutas
    API:                 str = ""
    PERFIL_ID:           str = ""
    # Opcional: backend JSON (vehículos, rutas /api/*). Si no va, ver resolve en config.py
    INTEGRACION_API_URL: str = ""

    @property
    def cors_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()