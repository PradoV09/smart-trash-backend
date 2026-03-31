from pydantic import BaseModel, ConfigDict
from models.model_roles import TipoRol


class ResponseRol(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_rol: int
    nombre: TipoRol

