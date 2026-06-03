# models/model_usuarios.py
"""Modelo ORM de usuarios.

Representa a las personas que interactúan con el sistema y conecta
la autenticación, el rol, el perfil y sus relaciones operativas.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Boolean


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    id_perfil  = Column(Integer, ForeignKey("perfiles.id_perfil"), nullable=False)
    id_rol     = Column(Integer, ForeignKey("roles.id_rol"), nullable=False)
    username   = Column(String(50), unique=True, nullable=False, index=True)
    correo     = Column(String(100), unique=True, nullable=False, index=True)
    contraseña = Column(String(255), nullable=False)
    activo     = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    perfil             = relationship("Perfil", back_populates="usuario")
    rol                = relationship("Rol", back_populates="usuarios")
    reportes_actividad = relationship("ReporteActividad")
    tripulaciones_legacy = relationship("TripulacionAsignacion", back_populates="usuario")
    miembros_tripulacion = relationship("TripulacionMiembro", back_populates="usuario")