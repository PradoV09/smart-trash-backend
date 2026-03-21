from fastapi import APIRouter
from controllers.controller_usuarios import router as usuarios_controller

router_usuarios = APIRouter()
router_usuarios.include_router(usuarios_controller)