# controllers/controller_usuarios.py

"""Controladores del módulo de usuarios.

Todos estos endpoints están pensados para administración y requieren AdminDep.
Los controllers solo orquestan la request y delegan la lógica al UsuarioService.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_usuarios import UsuarioAdminCreate, UsuarioUpdate, UsuarioResponse
from services.service_usuarios import UsuarioService
from models.model_usuarios import Usuario
import logging

logger = logging.getLogger(__name__)

async def crear_usuario(
    data: UsuarioAdminCreate = Depends(UsuarioAdminCreate.as_form),
    db: AsyncSession         = Depends(get_db),
    _: Usuario               = AdminDep,
) -> SuccessResponse[UsuarioResponse]:
    """Crea un usuario operativo o administrativo desde el panel de admin."""
    try:
        usuario = await UsuarioService(db).crear_por_admin(data)
        return success_response(data=usuario, message="Usuario creado exitosamente.")
    except Exception as e:
        logger.error(f"Error al crear usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el usuario: {str(e)}"
        )


async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    _: Usuario       = AdminDep,
) -> SuccessResponse[list[UsuarioResponse]]:
    """Lista todos los usuarios con sus relaciones de perfil y rol."""
    try:
        usuarios = await UsuarioService(db).obtener_todos_usuarios()
        return success_response(data=usuarios, message="Usuarios obtenidos exitosamente.")
    except Exception as e:
        logger.error(f"Error al listar usuarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la lista de usuarios."
        )


async def obtener_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario       = AdminDep,
) -> SuccessResponse[UsuarioResponse]:
    """Obtiene el detalle de un usuario específico por su id."""
    try:
        usuario = await UsuarioService(db).obtener_usuario_por_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
        return success_response(data=usuario, message="Usuario obtenido exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario {id_usuario}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el usuario."
        )


async def actualizar_usuario(
    id_usuario: int,
    data: UsuarioUpdate = Depends(UsuarioUpdate.as_form),
    db: AsyncSession    = Depends(get_db),
    _: Usuario          = AdminDep,
) -> SuccessResponse[UsuarioResponse]:
    """Actualiza parcialmente un usuario usando solo los campos enviados."""
    try:
        usuario = await UsuarioService(db).actualizar_usuario(id_usuario, data)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado para actualizar.")
        return success_response(data=usuario, message="Usuario actualizado exitosamente.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar usuario {id_usuario}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el usuario: {str(e)}"
        )


async def eliminar_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario       = AdminDep,
) -> SuccessResponse[dict[str, int]]:
    """Elimina un usuario del sistema por su id."""
    try:
        await UsuarioService(db).eliminar_usuario(id_usuario)
        return success_response(data={"id_usuario": id_usuario}, message="Usuario eliminado exitosamente.")
    except Exception as e:
        logger.error(f"Error al eliminar usuario {id_usuario}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el usuario."
        )