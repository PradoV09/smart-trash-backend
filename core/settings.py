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

    DATABASE_URL: str
    SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = (
        "http://localhost:4200,"
        "https://localhost,"
        "https://smart-trash-routes-production.up.railway.app,"
        "http://localhost:8100",
        "http://localhost:8101",
        "http://localhost",
        "https://localhost"
    )
    RUTAS_API_URL: str = "http://localhost:8001"  # URL de la API externa de rutas
    FRONTEND_URL: str = "http://localhost:4200"  # URL del frontend para reset password
    API: str = ""
    PERFIL_ID: str = ""
    # Opcional: backend JSON (vehículos, rutas /api/*). Si no va, ver resolve en config.py
    INTEGRACION_API_URL: str = ""

    # Configuración de Correo (Legacy SMTP - deprecated)
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # Configuración de Correo (Resend API)
    RESEND_API_KEY: str = ""

    @property
    def cors_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
