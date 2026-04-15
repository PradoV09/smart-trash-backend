# tests/test_api.py

import sys
from pathlib import Path
from urllib.parse import urlencode

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
def transport():
    return ASGITransport(app=app)


def form(data: dict) -> tuple[bytes, dict]:
    """Codifica un dict como application/x-www-form-urlencoded manejando ñ y caracteres especiales."""
    return (
        urlencode(data).encode("utf-8"),
        {"Content-Type": "application/x-www-form-urlencoded"},
    )


@pytest.mark.asyncio
async def test_root_returns_success(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


@pytest.mark.asyncio
async def test_login_campos_faltantes(transport):
    body, headers = form({"identifier": "admin"})  # sin contraseña
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/auth/login", content=body, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_credenciales_incorrectas(transport):
    body, headers = form({"identifier": "noexiste@mail.com", "contraseña": "wrong"})
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/auth/login", content=body, headers=headers)
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthorized"


@pytest.mark.asyncio
async def test_ruta_no_existe(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/no-existe")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_endpoint_protegido_sin_token(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/admin/usuarios")  # ✅ sin trailing slash, sin follow_redirects
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_endpoint_protegido_token_invalido(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(
            "/admin/usuarios",
            headers={"Authorization": "Bearer token_invalido"}
        )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthorized"


@pytest.mark.asyncio
async def test_vehiculos_sin_autenticacion(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/admin/vehiculos")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_health_check(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"