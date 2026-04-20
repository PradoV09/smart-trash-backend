# Esquema roles.py

from pydantic import BaseModel
from models.model_roles import TipoRol

class RolResponse(BaseModel):
    """Esquema para devolver la información de un rol."""
    id_rol: int
    nombre: TipoRol

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {"id_rol": 1, "nombre": "admin"}
        }