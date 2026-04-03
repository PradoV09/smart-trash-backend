# services/service_rutas_externo.py

"""Servicio para interactuar con la API externa de rutas.

Este servicio permite obtener rutas creadas en otra API (servicio de rutas).
"""

import httpx
from typing import Optional, Dict, Any
from core.settings import settings

class RutasExternoService:

    def __init__(self):
        # URL base de la API externa de rutas (configurar en settings)
        self.base_url = getattr(settings, 'RUTAS_API_URL', 'http://localhost:8001')  # Cambiar cuando tengas la API

    async def obtener_ruta_por_id(self, id_ruta: int) -> Optional[Dict[str, Any]]:
        """Obtiene los detalles de una ruta por su ID desde la API externa."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/rutas/{id_ruta}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    print(f"Error obteniendo ruta {id_ruta}: {response.status_code}")
                    return None
        except Exception as e:
            print(f"Error conectando con API de rutas: {e}")
            return None

    async def crear_ruta(self, datos_ruta: Dict[str, Any]) -> Optional[int]:
        """Crea una nueva ruta en la API externa y devuelve el ID."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{self.base_url}/rutas", json=datos_ruta)
                if response.status_code == 201:
                    data = response.json()
                    return data.get('id_ruta')  # Asumiendo que la respuesta tiene 'id_ruta'
                else:
                    print(f"Error creando ruta: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            print(f"Error conectando con API de rutas: {e}")
            return None

    async def validar_ruta_existe(self, id_ruta: int) -> bool:
        """Verifica si una ruta existe en la API externa."""
        ruta = await self.obtener_ruta_por_id(id_ruta)
        return ruta is not None