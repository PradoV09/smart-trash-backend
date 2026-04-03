"""Controladores del módulo de autenticación.

Su responsabilidad es recibir la request, resolver la sesión de base de datos
y delegar la lógica real a los servicios correspondientes.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_auth import LoginRequest, TokenResponse
from schemas.schema_usuarios import UsuarioPublicCreate, UsuarioResponse
from services.service_auth import AuthService
from services.service_usuarios import UsuarioService


async def login(data: LoginRequest = Depends(LoginRequest.as_form), db: AsyncSession = Depends(get_db)) -> SuccessResponse[TokenResponse]:
    """Autentica un usuario usando username o correo y devuelve un JWT."""
    token = await AuthService(db).login(data)
    return success_response(data=token, message="Inicio de sesión exitoso.")


async def registro_publico(data: UsuarioPublicCreate = Depends(UsuarioPublicCreate.as_form), db: AsyncSession = Depends(get_db)) -> UsuarioResponse:
    """Registra un usuario público con rol `user` asignado automáticamente."""
    usuario = await UsuarioService(db).registro_publico(data)
    return success_response(data=usuario, message="Usuario registrado exitosamente.")