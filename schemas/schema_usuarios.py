from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
import re
from schemas.schema_perfiles import PerfilResponse
from schemas.schema_roles import ResponseRol

class UsuarioAdminCreate(BaseModel):
    username:   str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    correo:     EmailStr = Field(..., description="Correo electrónico del usuario")
    contraseña: str = Field(..., min_length=6, description="Contraseña del usuario")
    id_rol:     int = Field(..., gt=0)  # solo driver o recolector
    activo:     Optional[bool] = True
    @field_validator('correo')
    @classmethod
    def validate_correo(cls, value):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(pattern, value):
            raise ValueError('Correo inválido')
        return value.lower()

class UsuarioPublicCreate(BaseModel):
    username:   str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    correo:      Optional[EmailStr] = Field(None, description="Correo electrónico del usuario")  # opcional para registro con Google
    contraseña: str = Field(..., min_length=6, description="Contraseña del usuario")
    activo:     Optional[bool] = True
    @field_validator('correo')
    @classmethod
    def validate_correo(cls, value):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(pattern, value):
            raise ValueError('Correo inválido')
        return value.lower()
    # rol y perfil se asignan automáticamente como "user"

class UsuarioUpdate(BaseModel):
    username:   str      | None = None
    correo:     EmailStr | None = None
    contraseña: str      | None = None
    id_rol:     int      | None = None
    @field_validator('correo')
    @classmethod
    def validate_correo(cls, value):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(pattern, value):
            raise ValueError('Correo inválido')
        return value.lower()

class UsuarioResponse(BaseModel):
    id_usuario: int
    username:   str
    correo:     EmailStr
    activo:     bool
    id_perfil:  int
    id_rol:     int
    perfil:     PerfilResponse
    rol:        ResponseRol
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)