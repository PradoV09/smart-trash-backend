from sqlalchemy.orm import Session
from models.model_usuarios import Usuario
from schemas.schema_usuarios import UsuarioCreate
from utils.security import hash_password

def get_usuarios(db: Session):
    return db.query(Usuario).all()

def get_usuario_by_id(db: Session, id_usuario: int):
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

def get_usuario_by_correo(db: Session, correo: str):
    return db.query(Usuario).filter(Usuario.correo == correo).first()

def create_usuario(db: Session, usuario: UsuarioCreate):
    existing = get_usuario_by_correo(db, usuario.correo)
    if existing:
        raise ValueError("El correo ya está registrado")
    db_usuario = Usuario(
        correo=usuario.correo,
        contraseña=hash_password(usuario.contraseña),
        id_perfil=usuario.id_perfil
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario