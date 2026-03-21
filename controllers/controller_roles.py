from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.connection import get_db
from schemas.schema_roles import RolCreate, ResponseRol
from services.service_roles import get_roles, get_rol_by_id, create_rol

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=list[ResponseRol])
def list_roles(db: Session = Depends(get_db)):
    return get_roles(db)

@router.get("/{id_rol}", response_model=ResponseRol)
def get_rol(id_rol: int, db: Session = Depends(get_db)):
    rol = get_rol_by_id(db, id_rol)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol

@router.post("/", response_model=ResponseRol, status_code=201)
def add_rol(rol: RolCreate, db: Session = Depends(get_db)):
    try:
        return create_rol(db, rol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))