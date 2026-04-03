# core/settings.py

from pydantic_settings import BaseSettings
from pydantic import ConfigDict          # ✅
from typing import List


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")  # ✅ reemplaza class Config

    DATABASE_URL:        str
    SECRET_KEY:          str
    JWT_SECRET:          str
    JWT_ALGORITHM:       str = "HS256"
    JWT_EXPIRE_MINUTES:  int = 480
    CORS_ORIGINS:        str = "http://localhost:4200"
    RUTAS_API_URL:       str = "http://localhost:8001"  # URL de la API externa de rutas

    @property
    def cors_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()