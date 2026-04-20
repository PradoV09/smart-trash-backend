# models/model_tripulacionasignacion.py

"""Modelo ORM de la tripulación asignada a cada recorrido."""

import enum
from sqlalchemy import Column, Enum, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class RolTripulacion(str, enum.Enum):
    piloto     = "piloto"
    copiloto   = "copiloto"
    recolector = "recolector"

class TripulacionAsignacion(Base):
    __tablename__ = "tripulacion_asignacion"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    rol_tripulacion = Column(Enum(RolTripulacion), nullable=False)
    confirmado      = Column(Boolean, default=False, nullable=False)
    confirmado_at   = Column(DateTime, nullable=True)

    asignacion = relationship("AsignacionRutas", back_populates="tripulacion")
    usuario    = relationship("Usuario", back_populates="tripulaciones")
