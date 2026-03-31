# routers/auth_router.py

from fastapi import APIRouter
from schemas.schema_auth import TokenResponse
from schemas.schema_usuarios import UsuarioPublicCreate, UsuarioResponse
from controllers import controller_auth

router = APIRouter(prefix="/auth", tags=["Auth"])

router.post("/login",    response_model=TokenResponse)(controller_auth.login)
router.post("/registro", response_model=UsuarioResponse)(controller_auth.registro_publico)