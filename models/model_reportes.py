# models/model_reportes.py

"""Modelo ORM de reportes y bitácora de actividad del sistema."""

from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class ReporteActividad(Base):
    __tablename__ = "ft_reporte_actividad"

    id_registro = Column(BigInteger, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    u_gmail_cache = Column(String(100), nullable=True)
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    asunto = Column(String(100), nullable=False)
    evidencia_url = Column(String(255), nullable=True)
    u_rol_cache = Column(String(20), nullable=True)

    usuario = relationship("Usuario", back_populates="reportes_actividad")