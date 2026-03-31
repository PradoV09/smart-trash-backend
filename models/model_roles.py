# models/model_roles.py

"""Modelo ORM del catálogo de roles del sistema."""

import enum
from sqlalchemy import Column, Enum, Integer
from sqlalchemy.orm import relationship
from database import Base

class TipoRol(str, enum.Enum):
    admin       = "admin"
    driver      = "driver"
    user        = "user"
    recolector  = "recolector"



class Rol(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Enum(TipoRol, name="tipo_rol"), nullable=False, unique=True)

    usuarios = relationship("Usuario", back_populates="rol")
    perfiles = relationship("Perfil", back_populates="rol")