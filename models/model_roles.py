from sqlalchemy import Column, Integer, String
from config.connection import Base

class Rol(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True)
    nombre = Column(String(20), nullable=False, unique=True)