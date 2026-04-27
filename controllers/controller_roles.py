from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from models.model_usuarios import Usuario
from core.dependecies import AdminDep, get_db
from core.response_builders import success_response
from schemas.schema_responses import SuccessResponse
from schemas.schema_roles import RolResponse
from services.service_roles import RoleService
import logging

logger = logging.getLogger(__name__)

async def obtener_todos_los_roles(
    db: AsyncSession = Depends(get_db),
    _: Usuario = AdminDep,
) -> SuccessResponse[list[RolResponse]]:
    """Obtiene el catálogo de roles para consumo del frontend administrativo."""
    try:
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
    except Exception as e:
        logger.error(f"Error al obtener roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el catálogo de roles."
        )