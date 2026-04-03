"""Schemas del módulo de usuarios.

Se usan para validar creación, actualización y serialización de usuarios,
perfiles y roles asociados.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
import re
from schemas.schema_perfiles import PerfilResponse
from schemas.schema_roles import ResponseRol
from fastapi import Form

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

    @classmethod
    def as_form(
        cls,
        username: str = Form(..., min_length=3, max_length=50),
        correo: EmailStr = Form(...),
        contraseña: str = Form(..., min_length=6),
        id_rol: int = Form(..., gt=0),
        activo: Optional[bool] = Form(True),
    ):
        return cls(
            username=username,
            correo=correo,
            contraseña=contraseña,
            id_rol=id_rol,
            activo=activo,
        )

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

    @classmethod
    def as_form(
        cls,
        username: str = Form(..., min_length=3, max_length=50),
        correo: Optional[EmailStr] = Form(None),
        contraseña: str = Form(..., min_length=6),
        activo: Optional[bool] = Form(True),
    ):
        return cls(
            username=username,
            correo=correo,
            contraseña=contraseña,
            activo=activo,
        )

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

    @classmethod
    def as_form(
        cls,
        username: Optional[str] = Form(None),
        correo: Optional[EmailStr] = Form(None),
        contraseña: Optional[str] = Form(None),
        id_rol: Optional[int] = Form(None),
    ):
        return cls(
            username=username,
            correo=correo,
            contraseña=contraseña,
            id_rol=id_rol,
        )

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