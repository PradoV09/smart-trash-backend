"""Servicio HTTP para integrar rutas y recorridos con API externa."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, status

from core.config import get_external_api_config
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
                detail="La variable 'API' no está configurada en .env.",
            )
        if not self.perfil_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La variable 'PERFIL_ID' no está configurada en .env.",
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

    async def iniciar_recorrido(self, data: IniciarRecorridoRequest) -> dict[str, Any]:
        self._validate_config()
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
        payload = {
            "lat": data.lat,
            "lon": data.lon,
            "perfil_id": self.perfil_id,
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
