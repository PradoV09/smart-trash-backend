from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.model_roles import Rol
from typing import List

class RoleService:
    """Servicio para la gestión del catálogo de roles."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar_roles(self) -> List[Rol]:
        """Obtiene todos los roles registrados en el sistema.
        
        Útil para llenar selectores en el frontend.
        """
        result = await self.db.execute(select(Rol))
        return list(result.scalars().all())