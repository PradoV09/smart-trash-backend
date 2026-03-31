"""Funciones de seguridad del proyecto.

Incluye hash de contraseñas con bcrypt y creación/validación de tokens JWT.
También expone una verificación async para no bloquear el event loop.
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from core.settings import settings
import asyncio
from functools import partial


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Versión async para evitar bloquear el event loop con operaciones de bcrypt.
async def verify_password_async(plain: str, hashed: str) -> bool:
    """Verifica la contraseña en un executor para mantener la API responsiva."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(pwd_context.verify, plain, hashed))

def crear_token(data: dict) -> str:
    """Genera un JWT firmado y agrega fecha de expiración automáticamente."""
    payload = data.copy()
    expira = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    payload.update({"exp": expira})
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verificar_token(token: str) -> dict | None:
    """Decodifica un JWT y devuelve el payload si es válido; si no, retorna `None`."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
