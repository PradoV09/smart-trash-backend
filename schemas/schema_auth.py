# schemas/schema_auth.py

"""Schemas del módulo de autenticación.

Definen el contrato de entrada para login y la respuesta con token JWT.
"""

from pydantic import BaseModel

class LoginRequest(BaseModel):
    identifier: str  # username o correo
    contraseña: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"