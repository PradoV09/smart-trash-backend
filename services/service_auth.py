
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status
from models.model_usuarios import Usuario
from schemas.schema_auth import LoginRequest, TokenResponse
from core.security import verify_password_async, crear_token

class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, data: LoginRequest) -> TokenResponse:
        result = await self.db.execute(
            select(Usuario).where(
                or_(
                    Usuario.username == data.identifier,
                    Usuario.correo   == data.identifier,
                )
            )
        )
        usuario = result.scalar_one_or_none()

        if not usuario or not await verify_password_async(data.contraseña, usuario.contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )

        token = crear_token({
            "sub": str(usuario.id_usuario),
            "rol": usuario.id_rol,
        })

        return TokenResponse(access_token=token)
