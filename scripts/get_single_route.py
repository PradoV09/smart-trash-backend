import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from services.service_api_externa import APIExternaService

async def get_single_route():
    service = APIExternaService()
    id_ruta = "a9733621-7f57-425e-be00-7c4312637e74"
    try:
        print(f"Consultando ruta {id_ruta} en: {service.api_base_url} (sin perfil_id)")
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{service.api_base_url}/api/rutas/{id_ruta}")
            print(f"Status: {resp.status_code}")
            print(f"Content-Type: {resp.headers.get('content-type')}")
            if resp.status_code == 200:
                print("Ruta encontrada:")
                print(resp.json())
            else:
                print(f"Error: {resp.text[:200]}")
    except Exception as e:
        print(f"Error consultando ruta: {e}")

if __name__ == "__main__":
    asyncio.run(get_single_route())
