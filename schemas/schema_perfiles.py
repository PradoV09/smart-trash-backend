"""Schemas relacionados con perfiles de usuario."""

from pydantic import BaseModel, Field, ConfigDict
from schemas.schema_roles import RolResponse


class PerfilResponse(BaseModel):
    id_perfil: int
    nombre:    str
    id_rol:    int
    rol:       RolResponse

    model_config = ConfigDict(from_attributes=True)