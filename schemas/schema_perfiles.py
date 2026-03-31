from pydantic import BaseModel, Field, ConfigDict
from schemas.schema_roles import ResponseRol


class PerfilResponse(BaseModel):
    id_perfil: int
    nombre:    str
    id_rol:    int
    rol:       ResponseRol

    model_config = ConfigDict(from_attributes=True)