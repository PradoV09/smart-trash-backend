from pydantic import BaseModel, ConfigDict

class RolCreate(BaseModel):
    nombre: str

class ResponseRol(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_rol: int
    nombre: str