"""
Servicio centralizado de sincronización bidireccional con API externa.

Este módulo proporciona una capa de abstracción uniforme para todas las operaciones
de sincronización entre la BD local y la API externa. Centraliza:

1. Lógica de sincronización CRUD
2. Manejo uniforme de errores (timeout, 4xx, 5xx)
3. Logging estructurado
4. Validación de respuestas
5. Metadata de sincronización

Principios:
- BD local es la fuente de verdad
- Si API externa falla, NO se pierden datos locales
- Operaciones son atómicas a nivel local primero
- Sincronización es asincrónica después
"""

from __future__ import annotations

import enum
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from dataclasses import dataclass, asdict

import httpx
from fastapi import HTTPException, status

from core.config import get_external_api_config
from models.model_vehiculo import EstadoVehiculo

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS Y DATACLASSES
# ============================================================================


class SyncStatus(str, enum.Enum):
    """Estados posibles de una operación de sincronización."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED_RECOVERABLE = "failed_recoverable"  # Reintentar
    FAILED_CRITICAL = "failed_critical"  # No reintentar


class SyncOperationType(str, enum.Enum):
    """Tipos de operaciones sincronizables."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncResourceType(str, enum.Enum):
    """Tipos de recursos a sincronizar."""

    VEHICULO = "vehiculo"
    ASIGNACION = "asignacion"
    POSICION = "posicion"
    TRIPULACION = "tripulacion"


@dataclass
class SyncMetadata:
    """Metadata de una operación de sincronización."""

    recurso_id: int
    recurso_tipo: SyncResourceType
    operacion: SyncOperationType
    estado: SyncStatus
    error_message: Optional[str] = None
    error_code: Optional[int] = None
    intentos: int = 1
    ultimo_intento: Optional[datetime] = None
    respuesta_externa: Optional[dict[str, Any]] = None
    id_externo: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convierte la metadata a diccionario para logging."""
        data = asdict(self)
        # Serializar enums
        data["recurso_tipo"] = self.recurso_tipo.value
        data["operacion"] = self.operacion.value
        data["estado"] = self.estado.value
        # Serializar datetime
        if self.ultimo_intento:
            data["ultimo_intento"] = self.ultimo_intento.isoformat()
        return data


# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================


class ExternalSyncException(Exception):
    """Excepción base para operaciones de sincronización."""

    pass


class ExternalSyncTimeoutException(ExternalSyncException):
    """Timeout en la API externa."""

    pass


class ExternalSyncNetworkException(ExternalSyncException):
    """Error de red/conexión con la API externa."""

    pass


class ExternalSync4xxException(ExternalSyncException):
    """Error 4xx en la API externa (cliente)."""

    pass


class ExternalSync5xxException(ExternalSyncException):
    """Error 5xx en la API externa (servidor)."""

    pass


# ============================================================================
# SERVICIO DE SINCRONIZACIÓN
# ============================================================================


class ExternalSyncService:
    """
    Servicio centralizado para sincronización bidireccional con API externa.

    Uso:
    ```python
    sync_service = ExternalSyncService()

    # Crear vehículo y sincronizar
    metadata = await sync_service.sync_create_vehiculo({
        "placa": "ABC-123",
        "modelo": "Volvo",
        "capacidad_m3": 10.0,
        "estado": "disponible"
    })

    if metadata.estado == SyncStatus.SUCCESS:
        id_externo = metadata.id_externo
    else:
        logger.error(f"Fallo en sincronización: {metadata.error_message}")
    ```
    """

    # Configuración de reintentos
    MAX_INTENTOS = 3
    TIMEOUT_SEGUNDOS = 30.0

    def __init__(self) -> None:
        """Inicializa el servicio y valida la configuración."""
        cfg = get_external_api_config()
        self.api_base_url = cfg.api_base_url
        self.perfil_id = cfg.perfil_id

        # Validar configuración mínima
        if not self.api_base_url:
            logger.warning(
                "ExternalSyncService: RUTAS_API_URL no configurada. "
                "La sincronización estará deshabilitada."
            )

    # ========================================================================
    # MÉTODOS PRIVADOS - UTILIDADES
    # ========================================================================

    def _validar_config(self) -> None:
        """Valida que la API externa esté configurada."""
        if not self.api_base_url:
            raise ExternalSyncException(
                "RUTAS_API_URL no está configurada. "
                "Configura la variable de entorno o .env"
            )

    def _validar_perfil_id(self) -> str:
        """Valida que el perfil_id esté configurado."""
        if not self.perfil_id:
            raise ExternalSyncException(
                "PERFIL_ID no está configurado. "
                "Configura la variable de entorno o .env"
            )
        return self.perfil_id

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        """Extrae mensaje de error de una respuesta HTTP."""
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
        return response.text or f"HTTP {response.status_code}"

    @staticmethod
    def _crear_metadata_error(
        recurso_id: int,
        recurso_tipo: SyncResourceType,
        operacion: SyncOperationType,
        error: Exception,
    ) -> SyncMetadata:
        """Crea metadata de error basada en la excepción."""
        estado = SyncStatus.FAILED_RECOVERABLE
        error_code = None

        if isinstance(error, ExternalSync4xxException):
            estado = SyncStatus.FAILED_CRITICAL  # Los 4xx no se reintentan
            error_code = 400
        elif isinstance(error, ExternalSync5xxException):
            estado = SyncStatus.FAILED_RECOVERABLE
            error_code = 500
        elif isinstance(error, ExternalSyncTimeoutException):
            estado = SyncStatus.FAILED_RECOVERABLE

        return SyncMetadata(
            recurso_id=recurso_id,
            recurso_tipo=recurso_tipo,
            operacion=operacion,
            estado=estado,
            error_message=str(error),
            error_code=error_code,
            ultimo_intento=datetime.now(timezone.utc),
        )

    async def _hacer_request(
        self,
        metodo: str,
        endpoint: str,
        json_payload: Optional[dict[str, Any]] = None,
        query_params: Optional[dict[str, str]] = None,
    ) -> tuple[int, dict[str, Any]]:
        """
        Realiza una petición HTTP a la API externa.

        Args:
            metodo: GET, POST, PATCH, DELETE
            endpoint: Ruta relativa (ej: "/api/vehiculos")
            json_payload: Datos a enviar en JSON
            query_params: Parámetros de query

        Returns:
            Tupla (status_code, response_json)

        Raises:
            ExternalSyncNetworkException: Error de conexión
            ExternalSyncTimeoutException: Timeout
            ExternalSync4xxException: Error 4xx
            ExternalSync5xxException: Error 5xx
        """
        url = f"{self.api_base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT_SEGUNDOS) as client:
                if metodo == "GET":
                    response = await client.get(url, params=query_params)
                elif metodo == "POST":
                    response = await client.post(
                        url, json=json_payload, params=query_params
                    )
                elif metodo == "PATCH":
                    response = await client.patch(
                        url, json=json_payload, params=query_params
                    )
                elif metodo == "DELETE":
                    response = await client.delete(url, params=query_params)
                else:
                    raise ValueError(f"Método HTTP no soportado: {metodo}")

                # Clasificar el error
                if 400 <= response.status_code < 500:
                    raise ExternalSync4xxException(
                        f"API externa respondió {response.status_code}: "
                        f"{self._extract_error_message(response)}"
                    )
                elif response.status_code >= 500:
                    raise ExternalSync5xxException(
                        f"API externa respondió {response.status_code}: "
                        f"{self._extract_error_message(response)}"
                    )

                try:
                    json_data = response.json()
                except (ValueError, httpx.ResponseNotRead):
                    json_data = {}

                return response.status_code, json_data

        except httpx.TimeoutException as e:
            raise ExternalSyncTimeoutException(f"Timeout en API externa: {e}") from e
        except httpx.NetworkError as e:
            raise ExternalSyncNetworkException(
                f"Error de conexión con API externa: {e}"
            ) from e
        except (
            ExternalSync4xxException,
            ExternalSync5xxException,
            ExternalSyncTimeoutException,
            ExternalSyncNetworkException,
        ):
            raise
        except Exception as e:
            raise ExternalSyncNetworkException(
                f"Error inesperado en API externa: {e}"
            ) from e

    # ========================================================================
    # MÉTODOS PÚBLICOS - VEHÍCULOS
    # ========================================================================

    async def sync_create_vehiculo(
        self,
        placa: str,
        modelo: Optional[str] = None,
        capacidad_m3: Optional[float] = None,
        estado: Optional[str] = None,
        recurso_id_local: Optional[int] = None,
    ) -> SyncMetadata:
        """
        Sincroniza la creación de un vehículo con la API externa.

        Args:
            placa: Placa del vehículo
            modelo: Modelo del vehículo
            capacidad_m3: Capacidad en m³
            estado: Estado operativo
            recurso_id_local: ID local del vehículo (opcional para logging)

        Returns:
            SyncMetadata con el resultado
        """
        recurso_id = recurso_id_local or 0
        try:
            self._validar_config()
            perfil_id = self._validar_perfil_id()

            payload = {
                "placa": placa,
                "perfil_id": perfil_id,
            }
            if modelo:
                payload["modelo"] = modelo
            if capacidad_m3 is not None:
                payload["capacidad_m3"] = capacidad_m3
            if estado:
                payload["estado"] = estado

            logger.info(f"[SYNC] Creando vehículo {placa} en API externa")
            status_code, response = await self._hacer_request(
                "POST", "/api/vehiculos", json_payload=payload
            )

            # Extraer ID externo
            id_externo = self._extract_vehiculo_id(response)

            logger.info(
                f"[SYNC] Vehículo {placa} creado exitosamente. ID externo: {id_externo}"
            )

            return SyncMetadata(
                recurso_id=recurso_id,
                recurso_tipo=SyncResourceType.VEHICULO,
                operacion=SyncOperationType.CREATE,
                estado=SyncStatus.SUCCESS,
                respuesta_externa=response,
                id_externo=id_externo,
                ultimo_intento=datetime.now(timezone.utc),
            )

        except ExternalSyncException as e:
            metadata = self._crear_metadata_error(
                recurso_id, SyncResourceType.VEHICULO, SyncOperationType.CREATE, e
            )
            logger.error(f"[SYNC ERROR] {metadata.to_dict()}")
            return metadata

    async def sync_update_vehiculo(
        self,
        id_externo: str,
        placa: Optional[str] = None,
        modelo: Optional[str] = None,
        capacidad_m3: Optional[float] = None,
        estado: Optional[str] = None,
        recurso_id_local: Optional[int] = None,
    ) -> SyncMetadata:
        """
        Sincroniza la actualización de un vehículo con la API externa.

        Args:
            id_externo: ID del vehículo en API externa
            placa: Placa del vehículo (opcional)
            modelo: Modelo (opcional)
            capacidad_m3: Capacidad (opcional)
            estado: Estado operativo (opcional)
            recurso_id_local: ID local (opcional para logging)

        Returns:
            SyncMetadata con el resultado
        """
        recurso_id = recurso_id_local or 0
        try:
            self._validar_config()
            perfil_id = self._validar_perfil_id()

            payload = {"perfil_id": perfil_id}
            if placa:
                payload["placa"] = placa
            if modelo is not None:
                payload["modelo"] = modelo
            if capacidad_m3 is not None:
                payload["capacidad_m3"] = capacidad_m3
            if estado:
                payload["estado"] = estado

            logger.info(f"[SYNC] Actualizando vehículo {id_externo} en API externa")
            status_code, response = await self._hacer_request(
                "PATCH", f"/api/vehiculos/{id_externo}", json_payload=payload
            )

            logger.info(f"[SYNC] Vehículo {id_externo} actualizado exitosamente")

            return SyncMetadata(
                recurso_id=recurso_id,
                recurso_tipo=SyncResourceType.VEHICULO,
                operacion=SyncOperationType.UPDATE,
                estado=SyncStatus.SUCCESS,
                respuesta_externa=response,
                id_externo=id_externo,
                ultimo_intento=datetime.now(timezone.utc),
            )

        except ExternalSyncException as e:
            metadata = self._crear_metadata_error(
                recurso_id, SyncResourceType.VEHICULO, SyncOperationType.UPDATE, e
            )
            logger.error(f"[SYNC ERROR] {metadata.to_dict()}")
            return metadata

    async def sync_delete_vehiculo(
        self,
        id_externo: str,
        recurso_id_local: Optional[int] = None,
    ) -> SyncMetadata:
        """
        Sincroniza la eliminación de un vehículo en la API externa.

        Args:
            id_externo: ID del vehículo en API externa
            recurso_id_local: ID local (opcional para logging)

        Returns:
            SyncMetadata con el resultado
        """
        recurso_id = recurso_id_local or 0
        try:
            self._validar_config()
            perfil_id = self._validar_perfil_id()

            logger.info(f"[SYNC] Eliminando vehículo {id_externo} en API externa")
            status_code, response = await self._hacer_request(
                "DELETE",
                f"/api/vehiculos/{id_externo}",
                query_params={"perfil_id": perfil_id},
            )

            logger.info(f"[SYNC] Vehículo {id_externo} eliminado exitosamente")

            return SyncMetadata(
                recurso_id=recurso_id,
                recurso_tipo=SyncResourceType.VEHICULO,
                operacion=SyncOperationType.DELETE,
                estado=SyncStatus.SUCCESS,
                respuesta_externa=response,
                id_externo=id_externo,
                ultimo_intento=datetime.now(timezone.utc),
            )

        except ExternalSyncException as e:
            metadata = self._crear_metadata_error(
                recurso_id, SyncResourceType.VEHICULO, SyncOperationType.DELETE, e
            )
            logger.error(f"[SYNC ERROR] {metadata.to_dict()}")
            return metadata

    # ========================================================================
    # MÉTODOS PÚBLICOS - POSICIONES
    # ========================================================================

    async def sync_create_posicion(
        self,
        recorrido_externo_id: str,
        latitud: float,
        longitud: float,
        perfil_id: Optional[str] = None,
        recurso_id_local: Optional[int] = None,
    ) -> SyncMetadata:
        """
        Sincroniza el registro de una posición GPS con la API externa.

        Args:
            recorrido_externo_id: ID del recorrido en API externa
            latitud: Latitud
            longitud: Longitud
            perfil_id: ID del perfil (opcional, usa configurado)
            recurso_id_local: ID local de la posición

        Returns:
            SyncMetadata con el resultado
        """
        recurso_id = recurso_id_local or 0
        try:
            self._validar_config()
            p_id = perfil_id or self._validar_perfil_id()

            payload = {
                "lat": float(latitud),
                "lon": float(longitud),
                "perfil_id": p_id,
            }

            logger.info(
                f"[SYNC] Registrando posición en recorrido {recorrido_externo_id} "
                f"({latitud}, {longitud})"
            )
            status_code, response = await self._hacer_request(
                "POST",
                f"/api/recorridos/{recorrido_externo_id}/posiciones",
                json_payload=payload,
            )

            logger.info(f"[SYNC] Posición registrada exitosamente")

            return SyncMetadata(
                recurso_id=recurso_id,
                recurso_tipo=SyncResourceType.POSICION,
                operacion=SyncOperationType.CREATE,
                estado=SyncStatus.SUCCESS,
                respuesta_externa=response,
                id_externo=recorrido_externo_id,
                ultimo_intento=datetime.now(timezone.utc),
            )

        except ExternalSyncException as e:
            metadata = self._crear_metadata_error(
                recurso_id, SyncResourceType.POSICION, SyncOperationType.CREATE, e
            )
            logger.error(f"[SYNC ERROR] {metadata.to_dict()}")
            return metadata

    # ========================================================================
    # MÉTODOS PÚBLICOS - ASIGNACIONES
    # ========================================================================

    async def sync_create_asignacion(
        self,
        ruta_id: str,
        vehiculo_id: str,
        perfil_id: Optional[str] = None,
        recurso_id_local: Optional[int] = None,
    ) -> SyncMetadata:
        """
        Sincroniza la creación de una asignación (recorrido) en API externa.

        Args:
            ruta_id: ID de la ruta en API externa
            vehiculo_id: ID del vehículo
            perfil_id: ID del perfil (opcional)
            recurso_id_local: ID local de la asignación

        Returns:
            SyncMetadata con el resultado (contiene recorrido_externo_id)
        """
        recurso_id = recurso_id_local or 0
        try:
            self._validar_config()
            p_id = perfil_id or self._validar_perfil_id()

            payload = {
                "ruta_id": str(ruta_id),
                "vehiculo_id": str(vehiculo_id),
                "perfil_id": p_id,
            }

            logger.info(f"[SYNC] Creando asignación en API externa (ruta={ruta_id})")
            status_code, response = await self._hacer_request(
                "POST", "/api/recorridos/iniciar", json_payload=payload
            )

            # Extraer ID del recorrido
            recorrido_id = response.get("id") or response.get("recorrido_id")

            logger.info(f"[SYNC] Asignación creada. Recorrido externo: {recorrido_id}")

            return SyncMetadata(
                recurso_id=recurso_id,
                recurso_tipo=SyncResourceType.ASIGNACION,
                operacion=SyncOperationType.CREATE,
                estado=SyncStatus.SUCCESS,
                respuesta_externa=response,
                id_externo=str(recorrido_id) if recorrido_id else None,
                ultimo_intento=datetime.now(timezone.utc),
            )

        except ExternalSyncException as e:
            metadata = self._crear_metadata_error(
                recurso_id, SyncResourceType.ASIGNACION, SyncOperationType.CREATE, e
            )
            logger.error(f"[SYNC ERROR] {metadata.to_dict()}")
            return metadata

    async def sync_finalizar_asignacion(
        self,
        recorrido_externo_id: str,
        perfil_id: Optional[str] = None,
        recurso_id_local: Optional[int] = None,
    ) -> SyncMetadata:
        """
        Sincroniza la finalización de una asignación en API externa.

        Args:
            recorrido_externo_id: ID del recorrido en API externa
            perfil_id: ID del perfil (opcional)
            recurso_id_local: ID local de la asignación

        Returns:
            SyncMetadata con el resultado
        """
        recurso_id = recurso_id_local or 0
        try:
            self._validar_config()
            p_id = perfil_id or self._validar_perfil_id()

            payload = {"perfil_id": p_id}

            logger.info(f"[SYNC] Finalizando recorrido {recorrido_externo_id}")
            status_code, response = await self._hacer_request(
                "POST",
                f"/api/recorridos/{recorrido_externo_id}/finalizar",
                json_payload=payload,
            )

            logger.info(f"[SYNC] Recorrido finalizado exitosamente")

            return SyncMetadata(
                recurso_id=recurso_id,
                recurso_tipo=SyncResourceType.ASIGNACION,
                operacion=SyncOperationType.UPDATE,
                estado=SyncStatus.SUCCESS,
                respuesta_externa=response,
                id_externo=recorrido_externo_id,
                ultimo_intento=datetime.now(timezone.utc),
            )

        except ExternalSyncException as e:
            metadata = self._crear_metadata_error(
                recurso_id, SyncResourceType.ASIGNACION, SyncOperationType.UPDATE, e
            )
            logger.error(f"[SYNC ERROR] {metadata.to_dict()}")
            return metadata

    # ========================================================================
    # UTILIDADES
    # ========================================================================

    @staticmethod
    def _extract_vehiculo_id(data: dict[str, Any]) -> str:
        """Extrae el ID de un vehículo desde respuesta de API."""
        for key in ("id", "vehiculo_id", "id_vehiculo", "uuid"):
            v = data.get(key)
            if v is not None:
                return str(v)

        nested = data.get("vehiculo")
        if isinstance(nested, dict) and nested.get("id"):
            return str(nested["id"])

        raise ExternalSync5xxException(
            "API externa no devolvió identificador de vehículo reconocible"
        )

    @staticmethod
    def _extract_recorrido_id(data: dict[str, Any]) -> str:
        """Extrae el ID de un recorrido desde respuesta de API."""
        for key in ("id", "recorrido_id", "id_recorrido", "uuid"):
            v = data.get(key)
            if v is not None:
                return str(v)

        raise ExternalSync5xxException(
            "API externa no devolvió identificador de recorrido reconocible"
        )

    def es_sincronizacion_habilitada(self) -> bool:
        """Verifica si la sincronización está habilitada."""
        return bool(self.api_base_url and self.perfil_id)


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================

_sync_service: Optional[ExternalSyncService] = None


def get_external_sync_service() -> ExternalSyncService:
    """Obtiene la instancia global del servicio de sincronización."""
    global _sync_service
    if _sync_service is None:
        _sync_service = ExternalSyncService()
    return _sync_service
