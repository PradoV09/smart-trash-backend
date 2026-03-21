from sqlalchemy.orm import Session
from models.model_roles import Rol
from schemas.schema_roles import RolCreate

def get_roles(db: Session):
    return db.query(Rol).all()

def get_rol_by_id(db: Session, id_rol: int):
    return db.query(Rol).filter(Rol.id_rol == id_rol).first()

def create_rol(db: Session, rol: RolCreate):
    existing = db.query(Rol).filter(Rol.nombre == rol.nombre).first()
    if existing:
        raise ValueError("El rol ya existe")
    db_rol = Rol(nombre=rol.nombre)
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol