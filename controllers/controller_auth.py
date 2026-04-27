"""Controladores del módulo de autenticación."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_auth import LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from services.service_auth import AuthService
import logging

logger = logging.getLogger(__name__)


async def login(data: LoginRequest = Depends(LoginRequest.as_form), db: AsyncSession = Depends(get_db)) -> SuccessResponse[TokenResponse]:
    """Autentica un usuario usando username o correo y devuelve un JWT."""
    try:
        token = await AuthService(db).login(data)
        return success_response(data=token, message="Inicio de sesión exitoso.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno durante el inicio de sesión."
        )

async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)) -> SuccessResponse[None]:
    """Inicia el flujo de recuperación de contraseña."""
    try:
        await AuthService(db).forgot_password(data)
        return success_response(data=None, message="Si el correo existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en forgot_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la solicitud de recuperación de contraseña."
        )

async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)) -> SuccessResponse[None]:
    """Restablece la contraseña con un token válido."""
    try:
        await AuthService(db).reset_password(data)
        return success_response(data=None, message="Contraseña actualizada exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reset_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al restablecer la contraseña."
        )