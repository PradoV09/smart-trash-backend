# schemas/schema_auth.py

"""Schemas del módulo de autenticación.

Definen el contrato de entrada para login y la respuesta con token JWT.
"""

from pydantic import BaseModel
from fastapi import Form

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