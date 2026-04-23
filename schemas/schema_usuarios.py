"""Schemas del módulo de usuarios.

Se usan para validar creación, actualización y serialización de usuarios,
perfiles y roles asociados.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
import re
from schemas.schema_perfiles import PerfilResponse
from schemas.schema_roles import RolResponse
from fastapi import Form

class UsuarioAdminCreate(BaseModel):
    nombre:     str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nombre del usuario (se guarda en el perfil; obligatorio)",
    )
    username:   str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    correo:     EmailStr = Field(..., description="Correo electrónico del usuario")
    contraseña: str = Field(..., min_length=6, description="Contraseña del usuario")
    id_rol:     int = Field(..., gt=0)  # solo driver o recolector
    activo:     Optional[bool] = True

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, value: str) -> str:
        s = value.strip()
        if not s:
            raise ValueError("El nombre del usuario es obligatorio y no puede ser solo espacios.")
        return s

    @field_validator('contraseña')
    @classmethod
    def validate_password_policy(cls, value):
        if len(value) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', value):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', value):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', value):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*()-_=+\[\]{}|;:\'",.<>/?`~]', value):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return value

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
        nombre: str = Form(..., min_length=1, max_length=255),
        username: str = Form(..., min_length=3, max_length=50),
        correo: EmailStr = Form(...),
        contraseña: str = Form(..., min_length=6),
        id_rol: int = Form(..., gt=0),
        activo: Optional[bool] = Form(True),
    ):
        return cls(
            nombre=nombre,
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

    @field_validator('contraseña')
    @classmethod
    def validate_password_policy(cls, value):
        if len(value) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', value):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', value):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', value):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*()-_=+\[\]{}|;:\'",.<>/?`~]', value):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return value
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
    activo:     bool     | None = None
    @field_validator('correo')
    @classmethod
    def validate_correo(cls, value):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(pattern, value):
            raise ValueError('Correo inválido')
        return value.lower()

    @field_validator('contraseña')
    @classmethod
    def validate_password_policy(cls, value):
        if value is None:
            return value
        if len(value) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', value):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', value):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', value):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*()-_=+\[\]{}|;:\'",.<>/?`~]', value):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return value

    @classmethod
    def as_form(
        cls,
        username: Optional[str] = Form(None),
        correo: Optional[EmailStr] = Form(None),
        contraseña: Optional[str] = Form(None),
        id_rol: Optional[int] = Form(None),
        activo: Optional[bool] = Form(None),
    ):
        return cls(
            username=username,
            correo=correo,
            contraseña=contraseña,
            id_rol=id_rol,
            activo=activo,
        )

# En schemas/schema_usuarios.py

class UsuarioResponse(BaseModel):
    id_usuario: int
    username:   str
    correo:     EmailStr
    activo:     bool
    id_perfil:  int
    id_rol:     int
    perfil:     PerfilResponse
    # Usa comillas para evitar la búsqueda inmediata del símbolo
    rol:        "RolResponse" 
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Esto fuerza a Pydantic a resolver el string "RolResponse" 
# contra el namespace real en tiempo de ejecución.
UsuarioResponse.model_rebuild()