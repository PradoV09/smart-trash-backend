# models/model_tripulacionasignacion.py

"""Modelo ORM de la tripulación asignada a cada recorrido."""

import enum
from sqlalchemy import Column, Enum, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class RolTripulacion(str, enum.Enum):
    conductor  = "conductor"
    recolector = "recolector"

class TripulacionAsignacion(Base):
    __tablename__ = "tripulacion_asignacion"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    id_asignacion   = Column(Integer, ForeignKey("asignaciones_rutas.id_asignacion"), nullable=False)
    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    rol_tripulacion = Column(Enum(RolTripulacion), nullable=False)
    confirmado      = Column(Boolean, default=False, nullable=False)
    confirmado_at   = Column(DateTime(timezone=True), nullable=True)

    asignacion_legacy = relationship("AsignacionRutas")
    usuario           = relationship("Usuario", back_populates="tripulaciones_legacy")
