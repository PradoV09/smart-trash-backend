from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.connection import Base

class Perfil(Base):
    __tablename__ = "perfiles"

    id_perfil = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    id_rol = Column(Integer, ForeignKey("roles.id_rol"), nullable=False)

    rol = relationship("Rol")
    usuario = relationship("Usuario", back_populates="perfil", uselist=False)