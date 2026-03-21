from pydantic import BaseModel, Field, ConfigDict

class PerfilCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre de la persona")
    id_rol: int = Field(..., description="ID del rol asignado")

class ResponsePerfil(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_perfil: int
    nombre: str
    id_rol: int