# models/model_perfiles.py

"""Modelo ORM de perfiles vinculados a los usuarios."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Perfil(Base):
    __tablename__ = "perfiles"

    id_perfil = Column(Integer, primary_key=True)
    id_rol = Column(Integer, ForeignKey("roles.id_rol"), nullable=False)
    nombre = Column(String(255), nullable=False)


    rol = relationship("Rol", back_populates="perfiles")
    usuario = relationship("Usuario", back_populates="perfil", uselist=False)