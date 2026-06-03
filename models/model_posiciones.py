"""Modelos ORM para posiciones GPS del recorrido.

Almacena las ubicaciones reportadas por los conductores durante un recorrido activo.
"""

import enum
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class RecorridoPosicion(Base):
    """Tabla de posiciones GPS reportadas durante un recorrido."""
    
    __tablename__ = "recorrido_posiciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    id_asignacion = Column(
        Integer,
        ForeignKey("asignaciones_rutas.id_asignacion", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)  # Precisión en metros
    speed = Column(Float, nullable=True)     # Velocidad en km/h
    bearing = Column(Float, nullable=True)   # Dirección en grados (0-360)
    timestamp = Column(DateTime(timezone=True), nullable=False)  # Timestamp del dispositivo
    imagen = Column(String(255), nullable=True)  # Ruta de la imagen asociada
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relación con asignación
    asignacion = relationship("AsignacionRutas", backref="posiciones")

    def __repr__(self):
        return f"<RecorridoPosicion(id={self.id}, lat={self.latitud}, lon={self.longitud})>"


# Índices para optimizar consultas frecuentes
Index(
    "ix_recorrido_posiciones_asignacion_timestamp",
    "id_asignacion",
    "timestamp"
)