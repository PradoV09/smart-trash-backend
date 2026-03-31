# routers/router_auth.py

from fastapi import APIRouter, status
from schemas.schema_auth import TokenResponse
from schemas.schema_responses import SuccessResponse
from schemas.schema_usuarios import UsuarioPublicCreate, UsuarioResponse
from controllers import controller_auth

router = APIRouter(prefix="/auth", tags=["Auth"])

router.post("/login",    response_model=SuccessResponse[TokenResponse])(controller_auth.login)
router.post("/registro", response_model=SuccessResponse[UsuarioResponse], status_code=status.HTTP_201_CREATED)(controller_auth.registro_publico)