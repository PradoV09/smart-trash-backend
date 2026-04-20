from fastapi import APIRouter, status
from controllers import controller_roles
from schemas.schema_responses import SuccessResponse
from schemas.schema_roles import RolResponse

router = APIRouter(prefix="/admin/roles", tags=["Admin - Roles"])

router.get(
    "",
    response_model=SuccessResponse[list[RolResponse]],
    status_code=status.HTTP_200_OK,
)(controller_roles.obtener_todos_los_roles)