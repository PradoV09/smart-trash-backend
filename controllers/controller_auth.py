"""Controladores del módulo de autenticación.

Su responsabilidad es recibir la request, resolver la sesión de base de datos
y delegar la lógica real a los servicios correspondientes.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_auth import LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from services.service_auth import AuthService


async def login(data: LoginRequest = Depends(LoginRequest.as_form), db: AsyncSession = Depends(get_db)) -> SuccessResponse[TokenResponse]:
    """Autentica un usuario usando username o correo y devuelve un JWT."""
    token = await AuthService(db).login(data)
    return success_response(data=token, message="Inicio de sesión exitoso.")

async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)) -> SuccessResponse[None]:
    """Inicia el flujo de recuperación de contraseña.
    
    TODO: Implementar Rate Limiting aquí (ej. máximo 3 intentos por hora por IP o correo)
    para mitigar ataques de enumeración o spam de correos.
    """
    await AuthService(db).forgot_password(data)
    return success_response(data=None, message="Si el correo existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña.")

async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)) -> SuccessResponse[None]:
    """Restablece la contraseña con un token válido.
    
    TODO: Implementar Rate Limiting aquí (ej. máximo 5 intentos por hora por IP)
    para mitigar ataques de fuerza bruta sobre el token.
    """
    await AuthService(db).reset_password(data)
    return success_response(data=None, message="Contraseña actualizada exitosamente.")