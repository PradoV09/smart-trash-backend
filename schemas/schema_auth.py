# schemas/auth.py

from pydantic import BaseModel

class LoginRequest(BaseModel):
    identifier: str  # username o correo
    contraseña: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"