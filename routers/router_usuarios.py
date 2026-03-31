# routers/router_usuarios.py

from fastapi import APIRouter, status
from schemas.schema_usuarios import UsuarioAdminCreate, UsuarioUpdate, UsuarioResponse
from controllers import controller_usuarios

router = APIRouter(prefix="/admin/usuarios", tags=["Usuarios"])

router.post("/",             response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)(controller_usuarios.crear_usuario)
router.get("/",              response_model=list[UsuarioResponse])(controller_usuarios.listar_usuarios)
router.get("/{id_usuario}",  response_model=UsuarioResponse)(controller_usuarios.obtener_usuario)
router.patch("/{id_usuario}", response_model=UsuarioResponse)(controller_usuarios.actualizar_usuario)
router.delete("/{id_usuario}")(controller_usuarios.eliminar_usuario)