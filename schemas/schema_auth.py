# schemas/schema_auth.py

"""Schemas del módulo de autenticación.

Definen el contrato de entrada para login y la respuesta con token JWT.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from fastapi import Form
import re

class LoginRequest(BaseModel):
    identifier: str  # username o correo
    contraseña: str

    @classmethod
    def as_form(
        cls,
        identifier: str = Form(...),
        contraseña: str = Form(...),
    ):
        return cls(identifier=identifier, contraseña=contraseña)

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"

class ForgotPasswordRequest(BaseModel):
    correo: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., description="La nueva contraseña")

    @field_validator('new_password')
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
