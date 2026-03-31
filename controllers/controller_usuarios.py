# controllers/controller_usuarios.py

"""Controladores del módulo de usuarios.

Todos estos endpoints están pensados para administración y requieren `AdminDep`.
Los controllers solo orquestan la request y delegan la lógica al `UsuarioService`.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from schemas.schema_usuarios import UsuarioAdminCreate, UsuarioUpdate, UsuarioResponse
from services.service_usuarios import UsuarioService
from models.model_usuarios import Usuario


async def crear_usuario(
    data: UsuarioAdminCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> UsuarioResponse:
    """Crea un usuario operativo o administrativo desde el panel de admin."""
    usuario = await UsuarioService(db).crear_por_admin(data)
    return success_response(data=usuario, message="Usuario creado exitosamente.")


async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> list[UsuarioResponse]:
    """Lista todos los usuarios con sus relaciones de perfil y rol."""
    usuarios = await UsuarioService(db).obtener_todos_usuarios()
    return success_response(data=usuarios, message="Usuarios obtenidos exitosamente.")


async def obtener_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> UsuarioResponse:
    """Obtiene el detalle de un usuario específico por su id."""
    usuario = await UsuarioService(db).obtener_usuario_por_id(id_usuario)
    return success_response(data=usuario, message="Usuario obtenido exitosamente.")


async def actualizar_usuario(
    id_usuario: int,
    data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> UsuarioResponse:
    """Actualiza parcialmente un usuario usando solo los campos enviados."""
    usuario = await UsuarioService(db).actualizar_usuario(id_usuario, data)
    return success_response(data=usuario, message="Usuario actualizado exitosamente.")


async def eliminar_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> dict:
    """Desactiva un usuario del sistema en lugar de borrarlo lógicamente."""
    await UsuarioService(db).eliminar_usuario(id_usuario)
    return success_response(data={"id_usuario": id_usuario}, message="Usuario desactivado exitosamente.")