import asyncio
import sys
from pathlib import Path

# Agregar la raíz del backend al path
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

from services.service_api_externa import APIExternaService

async def list_external_routes():
    service = APIExternaService()
    try:
        print(f"Consultando rutas en: {service.api_base_url}")
        print(f"Perfil ID: {service.perfil_id}")
        rutas = await service.listar_rutas()
        print("Rutas encontradas:")
        print(rutas)
    except Exception as e:
        print(f"Error consultando rutas: {e}")

if __name__ == "__main__":
    asyncio.run(list_external_routes())
