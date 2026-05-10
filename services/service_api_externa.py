"""Servicio HTTP para integrar rutas y recorridos con API externa."""

from __future__ import annotations

from typing import Any
import logging
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status

from core.config import get_external_api_config

logger = logging.getLogger(__name__)
from schemas.schema_recorridos_externos import (
    IniciarRecorridoRequest,
    RegistrarPosicionRequest,
)
from schemas.schema_rutas_externas import RutasCreateRequest
from models.model_vehiculo import EstadoVehiculo


class APIExternaService:
    def __init__(self) -> None:
        cfg = get_external_api_config()
        self.api_base_url = cfg.api_base_url
        self.perfil_id = cfg.perfil_id

    def _validate_config(self) -> None:
        if not self.api_base_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La variable 'RUTAS_API_URL' no está configurada en el archivo .env del backend.",
            )

    def _validate_perfil_id_config(self) -> None:
        if not self.perfil_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La variable 'PERFIL_ID' no está configurada en el archivo .env del backend.",
            )

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            data = response.json()
            if isinstance(data, dict):
                return (
                    data.get("detail")
                    or data.get("message")
                    or data.get("error")
                    or response.text
                )
        except Exception:
            pass
        return response.text or "Error de la API externa."

    @classmethod
    def _raise_external_error(cls, response: httpx.Response) -> None:
        raise HTTPException(
            status_code=response.status_code,
            detail=cls._extract_error_message(response),
        )

    async def crear_ruta(self, data: RutasCreateRequest) -> dict[str, Any]:
        self._validate_config()
        self._validate_perfil_id_config()
        payload: dict[str, Any] = {
            "nombre_ruta": data.nombre_ruta,
            "perfil_id": self.perfil_id,
        }
        if data.calles_ids:
            payload["calles_ids"] = [str(calle_id) for calle_id in data.calles_ids]
        elif data.shape is not None:
            payload["shape"] = data.shape

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(f"{self.api_base_url}/api/rutas", json=payload)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        return response.json()

    async def listar_rutas(self, perfil_id: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
        self._validate_config()
        p_id = perfil_id or self.perfil_id
        if not p_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo perfil_id es obligatorio.",
            )
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{self.api_base_url}/api/rutas",
                    params={"perfil_id": p_id},
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        return response.json()

    async def obtener_ruta(self, id: str, perfil_id: str | None = None) -> dict[str, Any]:
        self._validate_config()
        p_id = perfil_id or self.perfil_id
        if not p_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo perfil_id es obligatorio.",
            )
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{self.api_base_url}/api/rutas/{id}",
                    params={"perfil_id": p_id}
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        return response.json()

    async def iniciar_recorrido(self, data: IniciarRecorridoRequest) -> dict[str, Any]:
        self._validate_config()
        self._validate_perfil_id_config()
        payload = {
            "ruta_id": str(data.ruta_id),
            "vehiculo_id": str(data.vehiculo_id),
            "perfil_id": self.perfil_id,
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/api/recorridos/iniciar",
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        return response.json()

    async def registrar_posicion(
        self,
        recorrido_id: str,
        data: RegistrarPosicionRequest,
    ) -> dict[str, Any]:
        self._validate_config()
        p_id = str(data.perfil_id) if data.perfil_id else self.perfil_id
        if not p_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo perfil_id es obligatorio.",
            )
        payload = {
            "lat": data.lat,
            "lon": data.lon,
            "perfil_id": p_id,
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/api/recorridos/{recorrido_id}/posiciones",
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        return response.json()

    async def listar_posiciones_recorrido(
        self,
        recorrido_id: str,
        perfil_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        self._validate_config()
        p_id = perfil_id or self.perfil_id
        if not p_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo perfil_id es obligatorio.",
            )
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{self.api_base_url}/api/recorridos/{recorrido_id}/posiciones",
                    params={"perfil_id": p_id},
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        return response.json()

    @staticmethod
    def _extract_vehiculo_id(data: dict[str, Any]) -> str:
        for key in ("id", "vehiculo_id", "id_vehiculo"):
            v = data.get(key)
            if v is not None:
                return str(v)
        nested = data.get("vehiculo")
        if isinstance(nested, dict) and nested.get("id") is not None:
            return str(nested["id"])
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La API externa no devolvió un identificador de vehículo reconocible.",
        )

    # =========================================================================
    # MÉTODOS PARA INTEGRACIÓN DE RECORRIDOS CON API EXTERNA
    # =========================================================================

    async def iniciar_recorrido_externo(
        self,
        ruta_id: str,
        vehiculo_id: str,
        perfil_id: str | None = None,
    ) -> dict[str, Any]:
        """Inicia un recorrido en la API externa.
        
        Args:
            ruta_id: ID de la ruta en la API externa
            vehiculo_id: ID del vehículo
            perfil_id: ID del perfil (opcional, usa el configurado por defecto)
            
        Returns:
            dict: Respuesta con el ID del recorrido externo
        """
        self._validate_config()
        p_id = perfil_id or self.perfil_id
        if not p_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo perfil_id es obligatorio.",
            )
        
        payload = {
            "ruta_id": str(ruta_id),
            "vehiculo_id": str(vehiculo_id),
            "perfil_id": p_id,
        }
        
        full_url = f"{self.api_base_url}/api/recorridos/iniciar"
        logger.info(f"Llamando API externa para iniciar recorrido: {payload}")
        print(f"FULL URL: {full_url}")
        
                
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    full_url,
                    json=payload,
                    headers=headers
                )
        except httpx.RequestError as exc:
            logger.error(f"Error de conexión con API externa: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        # Debug: Print response details before parsing JSON
        print(f"STATUS: {response.status_code}")
        print(f"CONTENT: {response.text}")
        
        # Handle 201 (Created) as success response
        if response.status_code not in (200, 201):
            self._raise_external_error(response)
        
        if not response.content:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="La API externa devolvió respuesta vacía."
            )
        
        try:
            result = response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Respuesta no es JSON: {response.text}"
            )
        
        logger.info(f"Recorrido iniciado en API externa: {result}")
        return result

    async def finalizar_recorrido_externo(
        self,
        recorrido_externo_id: str,
        perfil_id: str | None = None,
    ) -> dict[str, Any]:
        """Finaliza un recorrido en la API externa.
        
        Args:
            recorrido_externo_id: ID del recorrido en la API externa
            perfil_id: ID del perfil (opcional)
            
        Returns:
            dict: Respuesta de la API externa
        """
        self._validate_config()
        p_id = perfil_id or self.perfil_id
        if not p_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El campo perfil_id es obligatorio.",
            )
        
        payload = {
            "perfil_id": p_id,
        }
        
        logger.info(f"Finalizando recorrido {recorrido_externo_id} en API externa")
        
                
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/api/recorridos/{recorrido_externo_id}/finalizar",
                    json=payload,
                    headers=headers
                )
        except httpx.RequestError as exc:
            logger.error(f"Error de conexión con API externa: {exc}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        
        result = response.json()
        logger.info(f"Recorrido finalizado en API externa: {result}")
        return result

    async def registrar_posicion_externa(
        self,
        recorrido_externo_id: str,
        latitud: float,
        longitud: float,
        perfil_id: str | None = None,
    ) -> dict[str, Any]:
        """Registra una posición en la API externa.
        
        Args:
            recorrido_externo_id: ID del recorrido
            latitud: Latitud
            longitud: Longitud
            perfil_id: ID del perfil
        """
        self._validate_config()
        p_id = perfil_id or self.perfil_id
        
        payload = {
            "lat": latitud,
            "lon": longitud,
            "perfil_id": p_id or self.perfil_id,
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/api/recorridos/{recorrido_externo_id}/posiciones",
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        return response.json()

    @staticmethod
    def _normalizar_lista_vehiculos(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]
        if isinstance(payload, dict):
            for key in ("data", "items", "vehiculos", "results"):
                inner = payload.get(key)
                if isinstance(inner, list):
                    return [x for x in inner if isinstance(x, dict)]
        return []

    async def crear_vehiculo_externo(
        self,
        *,
        placa: str,
        modelo: str | None,
        capacidad_m3: float | None,
        estado: EstadoVehiculo,
    ) -> tuple[str, dict[str, Any]]:
        """Crea vehículo en API externa. Devuelve (id_externo_uuid, respuesta_json)."""
        self._validate_config()
        self._validate_perfil_id_config()
        payload: dict[str, Any] = {
            "placa": placa,
            "perfil_id": self.perfil_id,
            "estado": estado.value,
        }
        if modelo is not None:
            payload["modelo"] = modelo
        if capacidad_m3 is not None:
            payload["capacidad_m3"] = capacidad_m3

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/api/vehiculos",
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        raw = response.json()
        if not isinstance(raw, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida al crear vehículo en la API externa.",
            )
        ext_id = self._extract_vehiculo_id(raw)
        return ext_id, raw

    async def listar_vehiculos_externos(self) -> list[dict[str, Any]]:
        """Obtiene el catálogo de vehículos desde la API externa."""
        self._validate_config()
        self._validate_perfil_id_config()
        params: dict[str, str] = {}
        if self.perfil_id:
            params["perfil_id"] = self.perfil_id
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{self.api_base_url}/api/vehiculos",
                    params=params or None,
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo conectar con la API externa: {exc}",
            ) from exc

        if response.is_error:
            self._raise_external_error(response)
        try:
            payload = response.json()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "La URL base no devolvió JSON en /api/vehiculos "
                    "(¿apunta al backend y no al visor SPA?)."
                ),
            )
        return self._normalizar_lista_vehiculos(payload)
