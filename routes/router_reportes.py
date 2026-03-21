from fastapi import APIRouter
from controllers.controller_reportes import router as reportes_controller

router_reportes = APIRouter()
router_reportes.include_router(reportes_controller)