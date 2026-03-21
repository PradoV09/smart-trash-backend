from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.connection import get_db
from schemas.schema_perfiles import PerfilCreate, ResponsePerfil
from services.service_perfiles import get_perfiles, get_perfil_by_id, create_perfil

router = APIRouter(prefix="/perfiles", tags=["Perfiles"])

@router.get("/", response_model=list[ResponsePerfil])
def list_perfiles(db: Session = Depends(get_db)):
    return get_perfiles(db)

@router.get("/{id_perfil}", response_model=ResponsePerfil)
def get_perfil(id_perfil: int, db: Session = Depends(get_db)):
    perfil = get_perfil_by_id(db, id_perfil)
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return perfil

@router.post("/", response_model=ResponsePerfil, status_code=201)
def add_perfil(perfil: PerfilCreate, db: Session = Depends(get_db)):
    try:
        return create_perfil(db, perfil)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))