from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from models.model_usuarios import Usuario
from models.model_perfiles import Perfil
from models.model_roles import Rol, TipoRol
from schemas.schema_usuarios import UsuarioAdminCreate, UsuarioPublicCreate, UsuarioUpdate
from core.security import hash_password

class UsuarioService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _check_duplicado(self, username: str, correo: str):
        result = await self.db.execute(
            select(Usuario).where(
                (Usuario.username == username) | (Usuario.correo == correo)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username o correo ya está en uso",
            )

    def _query_con_relaciones(self):
        return select(Usuario).options(
            selectinload(Usuario.perfil),
            selectinload(Usuario.rol),
        )

    async def crear_por_admin(self, data: UsuarioAdminCreate) -> Usuario:
        await self._check_duplicado(data.username, data.correo)

        # Verificar que el rol existe
        result = await self.db.execute(
            select(Rol).where(Rol.id_rol == data.id_rol)
        )
        rol = result.scalar_one_or_none()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol no encontrado",
            )

        # Crear perfil automáticamente
        perfil = Perfil(id_rol=rol.id_rol, nombre=data.username)
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

    async def registro_publico(self, data: UsuarioPublicCreate) -> Usuario:
        await self._check_duplicado(data.username, data.correo)

        result = await self.db.execute(
            select(Rol).where(Rol.nombre == TipoRol.user)
        )
        rol = result.scalar_one_or_none()
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Rol 'user' no configurado en el sistema",
            )

        perfil = Perfil(id_rol=rol.id_rol, nombre=data.username)
        self.db.add(perfil)
        await self.db.flush()

        usuario = Usuario(
            username=data.username,
            correo=data.correo,
            contraseña=hash_password(data.contraseña),
            id_rol=rol.id_rol,
            id_perfil=perfil.id_perfil,
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
                detail="Usuario no encontrado",
            )
        return usuario

    async def actualizar_usuario(self, id_usuario: int, data: UsuarioUpdate) -> Usuario:
        usuario = await self.obtener_usuario_por_id(id_usuario)
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
        usuario = await self.obtener_usuario_por_id(id_usuario)
        if usuario.rol.nombre == TipoRol.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un usuario con rol de administrador",
            )
        usuario.activo = False
        await self.db.flush()
        await self.db.commit()
        result = await self.db.execute(
            self._query_con_relaciones().where(Usuario.id_usuario == id_usuario)
        )
        return result.scalar_one()