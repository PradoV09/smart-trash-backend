from sqlalchemy.orm import Session
from models.model_perfiles import Perfil
from schemas.schema_perfiles import PerfilCreate

def get_perfiles(db: Session):
    return db.query(Perfil).all()

def get_perfil_by_id(db: Session, id_perfil: int):
    return db.query(Perfil).filter(Perfil.id_perfil == id_perfil).first()

def create_perfil(db: Session, perfil: PerfilCreate):
    db_perfil = Perfil(
        nombre=perfil.nombre,
        id_rol=perfil.id_rol
    )
    db.add(db_perfil)
    db.commit()
    db.refresh(db_perfil)
    return db_perfil