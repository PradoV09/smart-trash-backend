from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config.connection import get_db
from services.service_usuarios import get_usuario_by_correo
from utils.security import verify_password
from utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = get_usuario_by_correo(db, form_data.username)
    if not usuario:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    if not verify_password(form_data.password, usuario.contraseña):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    
    token = create_access_token(data={
        "sub": usuario.correo,
        "id": usuario.id_usuario,
        "perfil": usuario.id_perfil
    })
    return {"access_token": token, "token_type": "bearer"}