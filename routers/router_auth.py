# routers/router_auth.py

from fastapi import APIRouter
from schemas.schema_auth import TokenResponse
from schemas.schema_responses import SuccessResponse
from controllers import controller_auth

router = APIRouter(prefix="/auth", tags=["Autenticación"])

router.post("/login", response_model=SuccessResponse[TokenResponse])(controller_auth.login)
router.post("/forgot-password", response_model=SuccessResponse[None])(controller_auth.forgot_password)
router.post("/reset-password", response_model=SuccessResponse[None])(controller_auth.reset_password)