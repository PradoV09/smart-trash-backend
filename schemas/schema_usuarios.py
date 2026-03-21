from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

class UsuarioCreate(BaseModel):
    correo: str = Field(..., description="Correo electrónico del usuario")
    contraseña: str = Field(..., min_length=6, description="Contraseña del usuario")
    id_perfil: int = Field(..., description="ID del perfil asignado")

    @field_validator('correo')
    @classmethod
    def validate_correo(cls, value):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(pattern, value):
            raise ValueError('Correo inválido')
        return value.lower()

class ResponseUsuario(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_usuario: int
    correo: str
    id_perfil: int