# models/model_asignacionvehiculo.py

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
    id_tripulacion = Column(Integer, ForeignKey("tripulacion_asignacion.id"), nullable=True)  # opcional, se llena cuando se asigna tripulación
    hora_salida   = Column(DateTime, nullable=True)      # se llena cuando el driver inicia
    fecha         = Column(DateTime, nullable=False)
    estado        = Column(Enum(EstadoAsignacion), nullable=False, default=EstadoAsignacion.pendiente)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    vehiculo    = relationship("Vehiculo", back_populates="asignaciones")
    tripulacion = relationship("TripulacionAsignacion", back_populates="asignacion")