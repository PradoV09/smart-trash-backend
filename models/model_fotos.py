"""Modelos ORM para fotos/evidencia del recorrido.

Almacena imágenes capturadas por los conductores durante el recorrido:
- Recolección: Foto del contenedor lleno
- Incidencia: Foto de algún problema encontrado
- Cumplimiento: Foto que evidencia trabajo realizado
"""

import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class TipoFoto(str, enum.Enum):
    """Tipos de foto que se pueden capturar durante un recorrido."""
    recoleccion = "recoleccion"
    incidencia = "incidencia"
    cumplimiento = "cumplimiento"


class RecorridoFoto(Base):
    """Tabla de fotos/evidencia capturadas durante un recorrido."""
    
    __tablename__ = "recorrido_fotos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_asignacion = Column(
        Integer,
        ForeignKey("asignaciones_rutas.id_asignacion", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    url = Column(String(500), nullable=False)  # URL o path donde se almacena la imagen
    tipo = Column(Enum(TipoFoto), nullable=False)
    timestamp_captura = Column(DateTime(timezone=True), nullable=False)  # Cuando se tomó la foto
    timestamp_envio = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )  # Cuando se recibió en el servidor
    foto_metadata = Column("metadata", Text, nullable=True)  # JSON con info adicional (device, resolution, etc.)

    # Relación con asignación
    asignacion = relationship("AsignacionRutas", backref="fotos")

    def __repr__(self):
        return f"<RecorridoFoto(id={self.id}, tipo={self.tipo.value}, id_asignacion={self.id_asignacion})>"