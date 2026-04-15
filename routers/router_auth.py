# routers/router_auth.py

from fastapi import APIRouter
from schemas.schema_auth import TokenResponse
from schemas.schema_responses import SuccessResponse
from controllers import controller_auth

router = APIRouter(prefix="/auth", tags=["Auth"])

router.post("/login", response_model=SuccessResponse[TokenResponse])(controller_auth.login)