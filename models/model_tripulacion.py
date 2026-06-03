# models/model_tripulacion.py

"""Modelo ORM para la gestión de tripulaciones (equipos) independientes."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base
from models.model_asignaciontripulacion import RolTripulacion

class Tripulacion(Base):
    __tablename__ = "tripulaciones"

    id_tripulacion = Column(Integer, primary_key=True, autoincrement=True)
    nombre         = Column(String(100), nullable=True)
    created_at     = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relaciones
    miembros    = relationship("TripulacionMiembro", back_populates="tripulacion", cascade="all, delete-orphan")
    asignaciones = relationship("AsignacionRutas")

class TripulacionMiembro(Base):
    __tablename__ = "tripulacion_miembros"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    id_tripulacion  = Column(Integer, ForeignKey("tripulaciones.id_tripulacion"), nullable=False)
    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    rol_tripulacion = Column(Enum(RolTripulacion), nullable=False)
    confirmado      = Column(Boolean, default=False, nullable=False)
    confirmado_at   = Column(DateTime(timezone=True), nullable=True)

    tripulacion = relationship("Tripulacion", back_populates="miembros")
    usuario     = relationship("Usuario", back_populates="miembros_tripulacion")
