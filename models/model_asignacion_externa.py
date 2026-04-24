"""Modelos ORM para integración con API externa de recorridos.

Gestiona:
- AsignacionExterna: Vincula asignación local con recorrido externo
- IntentoPosicion: Registra intentos fallidos de sincronización de posiciones
"""

import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class EstadoExterno(str, enum.Enum):
    """Estados del recorrido en la API externa."""
    sincronizado = "sincronizado"
    pendiente = "pendiente"
    error = "error"


class EstadoIntento(str, enum.Enum):
    """Estados de los intentos de sincronización."""
    exitoso = "exitoso"
    fallido = "fallido"
    pendiente = "pendiente"


class AsignacionExterna(Base):
    """Vincula una asignación local con su correspondiente en la API externa."""
    
    __tablename__ = "asignaciones_externas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_asignacion = Column(
        Integer,
        ForeignKey("asignaciones_rutas.id_asignacion", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    recorrido_externo_id = Column(String(100), nullable=False)  # ID del recorrido en API externa
    estado_externo = Column(
        Enum(EstadoExterno),
        nullable=False,
        default=EstadoExterno.pendiente
    )
    ultima_sincro = Column(DateTime(timezone=True), nullable=True)  # Última sincronización exitosa
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relación con asignación
    asignacion = relationship("AsignacionRutas", backref="asignacion_externa")

    def __repr__(self):
        return f"<AsignacionExterna(id_asignacion={self.id_asignacion}, externo_id={self.recorrido_externo_id})>"


class IntentoPosicion(Base):
    """Registra intentos de sincronización de posiciones con la API externa."""
    
    __tablename__ = "intentos_posicion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_asignacion = Column(
        Integer,
        ForeignKey("asignaciones_rutas.id_asignacion", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    payload = Column(Text, nullable=False)  # JSON con los datos de posición
    estado = Column(Enum(EstadoIntento), nullable=False, default=EstadoIntento.pendiente)
    error_msg = Column(Text, nullable=True)  # Mensaje de error si falló
    retry_count = Column(Integer, default=0, nullable=False)  # Número de reintentos
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relación con asignación
    asignacion = relationship("AsignacionRutas", backref="intentos_posicion")

    def __repr__(self):
        return f"<IntentoPosicion(id={self.id}, id_asignacion={self.id_asignacion}, estado={self.estado.value})>"


# Índices para optimizar consultas
Index("ix_intentos_posicion_asignacion_estado", "id_asignacion", "estado")
Index("ix_intentos_posicion_created_at", "created_at")