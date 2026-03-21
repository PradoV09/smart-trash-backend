from fastapi import APIRouter
from controllers.controller_perfiles import router as perfiles_controller

router_perfiles = APIRouter()
router_perfiles.include_router(perfiles_controller)