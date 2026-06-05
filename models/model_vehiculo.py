# models/model_vehiculo.py

"""Modelo ORM de vehículos y catálogo de estados operativos."""

import enum
from sqlalchemy import Column, Enum, Float, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class EstadoVehiculo(str, enum.Enum):
    disponible    = "disponible"
    en_ruta       = "en_ruta"
    mantenimiento = "mantenimiento"
    inactivo      = "inactivo"

class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id_vehiculo  = Column(Integer, primary_key=True, autoincrement=True)
    id_externo   = Column(String(36), unique=True, nullable=True, index=True)
    placa        = Column(String(20), unique=True, nullable=False)
    marca        = Column(String(100), nullable=True)
    modelo       = Column(String(100), nullable=True)
    capacidad_m3 = Column(Float, nullable=True)
    estado       = Column(Enum(EstadoVehiculo), nullable=False, default=EstadoVehiculo.disponible)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    asignaciones = relationship("AsignacionRutas")