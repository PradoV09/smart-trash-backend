from fastapi import APIRouter
from controllers.controller_users import router as users_controller

router_users = APIRouter()
router_users.include_router(users_controller)