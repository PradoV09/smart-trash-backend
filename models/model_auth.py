"""Modelo ORM para recuperación de contraseña.

Contiene la estructura para almacenar tokens seguros de recuperación.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from database import Base

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
