from fastapi import APIRouter
from controllers.controller_roles import router as roles_controller

router_roles = APIRouter()
router_roles.include_router(roles_controller)