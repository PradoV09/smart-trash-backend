"""Servicios de autenticación.

Aquí vive la lógica para validar credenciales y emitir tokens JWT.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from models.model_usuarios import Usuario
from models.model_roles import Rol, TipoRol
from core.security import verify_password_async, crear_token, hash_password
from core.settings import settings
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from models.model_auth import PasswordReset
from schemas.schema_auth import LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from core.email import enviar_correo_async


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Autentica un usuario y genera su token de acceso.

        Pasos:
        1. Busca por username o correo (con relación de rol cargada).
        2. Verifica la contraseña con la versión async.
        3. Rechaza usuarios con rol 'user' (no tienen acceso de autenticación).
        4. Genera un JWT con id, rol y `username` (mismo valor que en BD / columna Usuario).
        """
        result = await self.db.execute(
            select(Usuario)
            .options(selectinload(Usuario.rol))
            .where(
                or_(
                    Usuario.username == data.identifier,
                    Usuario.correo   == data.identifier,
                )
            )
        )
        usuario = result.scalar_one_or_none()

        # Si el usuario no existe o la contraseña no coincide, se rechaza el acceso.
        if not usuario or not await verify_password_async(data.contraseña, usuario.contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas. Verifica el identificador y la contraseña e inténtalo de nuevo.",
            )

        # Los usuarios con rol 'user' (públicos) no tienen acceso de autenticación.
        if usuario.rol.nombre == TipoRol.user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Los usuarios públicos no tienen permiso para autenticarse en el sistema.",
            )

        # Incluye `username` para que clientes/listas coincidan con el valor guardado al crear el usuario.
        token = crear_token({
            "sub": str(usuario.id_usuario),
            "rol": usuario.id_rol,
            "username": usuario.username,
            "perfil_id": settings.PERFIL_ID,
        })

        return TokenResponse(access_token=token)

    async def forgot_password(self, data: ForgotPasswordRequest, background_tasks) -> None:
        """Procesa la solicitud de recuperación de contraseña.
        
        Siempre retorna exitosamente para evitar enumeración de usuarios.
        """
        # Buscar usuario activo por correo
        result = await self.db.execute(
            select(Usuario).where(Usuario.correo == data.correo, Usuario.activo == True)
        )
        usuario = result.scalar_one_or_none()

        if usuario:
            # Generar token seguro (32 bytes)
            raw_token = secrets.token_urlsafe(32)
            
            # Hashear el token con SHA-256 para almacenarlo
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            
            # Establecer expiración (15 minutos)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
            
            # Guardar en base de datos
            reset_record = PasswordReset(
                id_usuario=usuario.id_usuario,
                token_hash=token_hash,
                expires_at=expires_at
            )
            self.db.add(reset_record)
            await self.db.commit()
            
            # Enviar correo en background para no bloquear la respuesta
            background_tasks.add_task(enviar_correo_async, usuario.correo, raw_token)
            
        # El endpoint siempre debe retornar lo mismo independientemente de si el usuario existe

    async def reset_password(self, data: ResetPasswordRequest) -> None:
        """Restablece la contraseña utilizando el token enviado."""
        # Hashear el token recibido para buscarlo
        token_hash = hashlib.sha256(data.token.encode()).hexdigest()
        
        # Buscar el token en la BD
        result = await self.db.execute(
            select(PasswordReset).where(PasswordReset.token_hash == token_hash)
        )
        reset_record = result.scalar_one_or_none()
        
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado."
            )
            
        # Verificar expiración
        if datetime.now(timezone.utc) > reset_record.expires_at:
            # Eliminar token expirado por limpieza
            await self.db.delete(reset_record)
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado."
            )
            
        # Buscar el usuario y actualizar contraseña
        result_user = await self.db.execute(
            select(Usuario).where(Usuario.id_usuario == reset_record.id_usuario, Usuario.activo == True)
        )
        usuario = result_user.scalar_one_or_none()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no válido."
            )
            
        # Hashear nueva contraseña y actualizar
        usuario.contraseña = hash_password(data.new_password)
        
        # El updated_at se actualiza automáticamente según el modelo,
        # pero podemos forzarlo si no está configurado en onupdate
        # usuario.updated_at = datetime.now(timezone.utc)
        
        # Eliminar el token usado (un solo uso)
        await self.db.delete(reset_record)
        await self.db.commit()
