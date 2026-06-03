# models/model_asignacionrutas.py

"""Modelo ORM de asignaciones entre vehículos y rutas externas."""

import enum
from sqlalchemy import Column, Enum, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class EstadoAsignacion(str, enum.Enum):
    pendiente  = "pendiente"
    en_curso   = "en_curso"
    completada = "completada"
    cancelada  = "cancelada"

class AsignacionRutas(Base):
    __tablename__ = "asignaciones_rutas"

    id_asignacion = Column(Integer, primary_key=True, autoincrement=True)
    id_vehiculo   = Column(Integer, ForeignKey("vehiculos.id_vehiculo"), nullable=False)
    id_ruta       = Column(String(100), nullable=False)  # ID externo de la API de rutas
    id_tripulacion = Column(Integer, ForeignKey("tripulaciones.id_tripulacion"), nullable=True)
    hora_salida   = Column(DateTime(timezone=True), nullable=True)      # se llena cuando el driver inicia
    fecha         = Column(DateTime(timezone=True), nullable=False)
    estado        = Column(Enum(EstadoAsignacion), nullable=False, default=EstadoAsignacion.pendiente)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships without back_populates to avoid circular dependencies
    vehiculo    = relationship("Vehiculo")
    tripulacion = relationship("Tripulacion")