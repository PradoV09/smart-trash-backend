from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from models.model_usuarios import Usuario
from core.dependecies import AdminDep, get_db
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_roles import RolResponse
from services.service_roles import RoleService

async def obtener_todos_los_roles(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[RolResponse]]:
    """Obtiene el catálogo de roles para consumo del frontend administrativo."""
    service = RoleService(db)
    roles = await service.listar_roles()
    if not roles:
        return success_response(
            data=[],
            message="No se encontraron roles configurados.",
        )

    return success_response(
        data=roles,
        message="Catálogo de roles obtenido exitosamente.",
    )