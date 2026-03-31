from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db
from schemas.schema_auth import LoginRequest, TokenResponse
from schemas.schema_usuarios import UsuarioPublicCreate, UsuarioResponse
from services.service_auth import AuthService
from services.service_usuarios import UsuarioService

async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    return await AuthService(db).login(data)

async def registro_publico(data: UsuarioPublicCreate, db: AsyncSession = Depends(get_db)) -> UsuarioResponse:
    return await UsuarioService(db).registro_publico(data)