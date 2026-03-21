from fastapi import APIRouter
from controllers.controller_auth import router as auth_controller

router_auth = APIRouter()
router_auth.include_router(auth_controller)