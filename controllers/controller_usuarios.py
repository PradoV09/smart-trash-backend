from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.connection import get_db
from schemas.schema_usuarios import UsuarioCreate, ResponseUsuario
from services.service_usuarios import get_usuarios, get_usuario_by_id, create_usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", response_model=list[ResponseUsuario])
def list_usuarios(db: Session = Depends(get_db)):
    return get_usuarios(db)

@router.get("/{id_usuario}", response_model=ResponseUsuario)
def get_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = get_usuario_by_id(db, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.post("/", response_model=ResponseUsuario, status_code=201)
def add_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return create_usuario(db, usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))