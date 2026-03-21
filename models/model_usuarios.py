from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from config.connection import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True)
    correo = Column(String(100), unique=True, nullable=False, index=True)
    contraseña = Column(String(255), nullable=False)
    id_perfil = Column(Integer, ForeignKey("perfiles.id_perfil"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    perfil = relationship("Perfil", back_populates="usuario")