"""Servicios del módulo de usuarios.

Contiene la lógica para crear, consultar, actualizar y desactivar usuarios,
incluyendo validaciones de rol, duplicados y hash de contraseñas.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from models.model_usuarios import Usuario
from models.model_perfiles import Perfil
from models.model_roles import Rol, TipoRol
from schemas.schema_usuarios import UsuarioAdminCreate, UsuarioUpdate
from core.security import hash_password


class UsuarioService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _check_duplicado(self, username: str, correo: str):
        """Valida que no exista otro usuario con el mismo username o correo."""
        result = await self.db.execute(
            select(Usuario).where(
                (Usuario.username == username) | (Usuario.correo == correo)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un usuario registrado con el username '{username}' o el correo '{correo}'.",
            )

    def _query_con_relaciones(self):
        """Construye una consulta que precarga `perfil` y `rol`.

        Esto evita cargas diferidas innecesarias y facilita serializar respuestas.
        """
        return select(Usuario).options(
            selectinload(Usuario.perfil),
            selectinload(Usuario.rol),
        )

    async def crear_por_admin(self, data: UsuarioAdminCreate) -> Usuario:
        """Crea un usuario desde administración y le genera su perfil asociado."""
        await self._check_duplicado(data.username, data.correo)

        # Primero se valida que el rol destino exista en la tabla catálogo.
        result = await self.db.execute(
            select(Rol).where(Rol.id_rol == data.id_rol)
        )
        rol = result.scalar_one_or_none()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se encontró un rol con id {data.id_rol}. Verifica el catálogo de roles.",
            )

        # Validar que el rol sea uno de los permitidos para creación por admin
        roles_permitidos = {TipoRol.admin, TipoRol.driver, TipoRol.recolector}
        if rol.nombre not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"El rol '{rol.nombre.value}' no puede ser asignado por un administrador. "
                       f"Solo se permiten los roles: admin, driver, recolector.",
            )

        # El perfil se crea automáticamente para mantener sincronizada la relación usuario-perfil.
        perfil = Perfil(id_rol=rol.id_rol, nombre=data.nombre)
        self.db.add(perfil)
        await self.db.flush()

        usuario = Usuario(
            username=data.username,
            correo=data.correo,
            contraseña=hash_password(data.contraseña),
            id_perfil=perfil.id_perfil,
            id_rol=rol.id_rol,
            activo=data.activo,
        )
        self.db.add(usuario)
        await self.db.flush()
        await self.db.commit()
        result = await self.db.execute(
            self._query_con_relaciones().where(Usuario.id_usuario == usuario.id_usuario)
        )
        return result.scalar_one()

    async def obtener_todos_usuarios(self) -> list[Usuario]:
        result = await self.db.execute(self._query_con_relaciones())
        return result.scalars().all()

    async def obtener_usuario_por_id(self, id_usuario: int) -> Usuario:
        result = await self.db.execute(
            self._query_con_relaciones().where(Usuario.id_usuario == id_usuario)
        )
        usuario = result.scalar_one_or_none()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un usuario con id {id_usuario}.",
            )
        return usuario

    async def actualizar_usuario(self, id_usuario: int, data: UsuarioUpdate) -> Usuario:
        """Actualiza solo los campos presentes en el payload.

        Si la contraseña cambia, vuelve a hashearse antes de guardarla.
        Si se cambia el rol, valida que sea uno de los permitidos.
        """
        usuario = await self.obtener_usuario_por_id(id_usuario)

        # Si se está actualizando el rol, validar que sea permitido
        if data.id_rol is not None:
            result = await self.db.execute(
                select(Rol).where(Rol.id_rol == data.id_rol)
            )
            rol = result.scalar_one_or_none()
            if not rol:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se encontró un rol con id {data.id_rol}.",
                )
            roles_permitidos = {TipoRol.admin, TipoRol.driver, TipoRol.recolector}
            if rol.nombre not in roles_permitidos:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"El rol '{rol.nombre.value}' no puede ser asignado por un administrador. "
                           f"Solo se permiten los roles: admin, driver, recolector.",
                )

        for campo, valor in data.model_dump(exclude_none=True).items():
            if campo == "contraseña":
                valor = hash_password(valor)
            setattr(usuario, campo, valor)
        await self.db.flush()
        await self.db.commit()
        result = await self.db.execute(
            self._query_con_relaciones().where(Usuario.id_usuario == id_usuario)
        )
        return result.scalar_one()

    async def eliminar_usuario(self, id_usuario: int):
        """Desactiva lógicamente un usuario (activo=False); no borra la fila por integridad referencial."""
        usuario = await self.obtener_usuario_por_id(id_usuario)
        usuario.activo = False
        await self.db.flush()