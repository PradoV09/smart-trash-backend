import asyncio
from fastapi import FastAPI, APIRouter, Request
from fastapi.testclient import TestClient

app = FastAPI()

router_legacy = APIRouter(prefix="/api/uploads/fotos")
@router_legacy.get("/{filename}")
def get_foto_legacy(filename: str):
    return {"foto_legacy": filename}

app.include_router(router_legacy, prefix="/api")

client = TestClient(app)

print("GET /api/api/uploads/fotos/13.png ->", client.get("/api/api/uploads/fotos/13.png").status_code)
