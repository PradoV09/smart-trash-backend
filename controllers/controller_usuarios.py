# controllers/usuario_controller.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from schemas.schema_usuarios import UsuarioAdminCreate, UsuarioUpdate, UsuarioResponse
from services.service_usuarios import UsuarioService
from models.model_usuarios import Usuario

async def crear_usuario(
    data: UsuarioAdminCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> UsuarioResponse:
    return await UsuarioService(db).crear_por_admin(data)

async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[UsuarioResponse]:
    return await UsuarioService(db).obtener_todos_usuarios()

async def obtener_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> UsuarioResponse:
    return await UsuarioService(db).obtener_usuario_por_id(id_usuario)

async def actualizar_usuario(
    id_usuario: int,
    data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> UsuarioResponse:
    return await UsuarioService(db).actualizar_usuario(id_usuario, data)

async def eliminar_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> dict:
    await UsuarioService(db).eliminar_usuario(id_usuario)
    return {"message": "Usuario eliminado"}