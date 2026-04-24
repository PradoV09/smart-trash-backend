# core/websocket_manager.py

"""Administrador simple de conexiones WebSocket agrupadas por asignación.

Permite que varios clientes se suscriban al estado de una misma asignación
para recibir eventos en tiempo real cuando el recorrido cambia de estado.
"""

from fastapi import WebSocket
from typing import DefaultDict
from collections import defaultdict
import asyncio
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class WebSocketManager:

    def __init__(self):
        # agrupa conexiones por id_asignacion
        self.conexiones: DefaultDict[int, list[WebSocket]] = defaultdict(list)
        # tareas periódicas para actualizaciones en vivo
        self.tareas_periodicas: dict[int, asyncio.Task] = {}

    async def conectar(self, websocket: WebSocket, id_asignacion: int):
        """Acepta una conexión nueva y la asocia al grupo de una asignación."""
        await websocket.accept()
        self.conexiones[id_asignacion].append(websocket)
        
        # Iniciar tarea periódica si es la primera conexión para esta asignación
        if id_asignacion not in self.tareas_periodicas:
            await self._iniciar_actualizaciones_periodicas(id_asignacion)

    def desconectar(self, websocket: WebSocket, id_asignacion: int):
        """Remueve una conexión cuando el cliente se desconecta."""
        if id_asignacion in self.conexiones and websocket in self.conexiones[id_asignacion]:
            self.conexiones[id_asignacion].remove(websocket)

            # Si no quedan conexiones para esta asignación, limpiar el diccionario
            if not self.conexiones[id_asignacion]:
                del self.conexiones[id_asignacion]
                # Cancelar tarea periódica
                if id_asignacion in self.tareas_periodicas:
                    self.tareas_periodicas[id_asignacion].cancel()
                    del self.tareas_periodicas[id_asignacion]

    async def _iniciar_actualizaciones_periodicas(self, id_asignacion: int):
        """Inicia tarea periódica para enviar actualizaciones cada 5 segundos."""
        
        async def enviar_actualizaciones():
            while True:
                try:
                    # Enviar evento de posición actualizada
                    await self.broadcast(id_asignacion, {
                        "evento": "posicion_actualizada",
                        "id_asignacion": id_asignacion,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "data": {
                            "lat": None,  # Se obtendrá de la última posición en BD
                            "lon": None,
                            "velocidad": None,
                            "ultimo_hito": None
                        }
                    })
                    
                    # Esperar 5 segundos para la próxima actualización
                    await asyncio.sleep(5)
                    
                except asyncio.CancelledError:
                    logger.info(f"Tarea periódica cancelada para asignación {id_asignacion}")
                    break
                except Exception as e:
                    logger.error(f"Error en actualización periódica para asignación {id_asignacion}: {e}")
                    await asyncio.sleep(5)

        self.tareas_periodicas[id_asignacion] = asyncio.create_task(enviar_actualizaciones())

    async def emitir_posicion_actualizada(self, id_asignacion: int, posicion_data: dict):
        """Emite evento de posición actualizada inmediatamente."""
        await self.broadcast(id_asignacion, {
            "evento": "posicion_actualizada",
            "id_asignacion": id_asignacion,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": posicion_data
        })

    async def emitir_cambio_estado(self, id_asignacion: int, estado_anterior: str, estado_nuevo: str):
        """Emite evento de cambio de estado."""
        await self.broadcast(id_asignacion, {
            "evento": "estado_cambio",
            "id_asignacion": id_asignacion,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "estado_anterior": estado_anterior,
                "estado_nuevo": estado_nuevo
            }
        })

    async def emitir_evento_tripulacion(self, id_asignacion: int, tipo_evento: str, usuario_data: dict):
        """Emite evento relacionado con la tripulación."""
        await self.broadcast(id_asignacion, {
            "evento": "tripulacion_evento",
            "id_asignacion": id_asignacion,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "tipo": tipo_evento,
                "usuario": usuario_data
            }
        })

    async def broadcast(self, id_asignacion: int, mensaje: dict):
        """Envía un mensaje JSON a todos los clientes conectados a una asignación."""
        conexiones = self.conexiones.get(id_asignacion, [])
        if not conexiones:
            return  # No hay conexiones para esta asignación

        # Crear una copia para evitar problemas de modificación durante iteración
        conexiones_activas = conexiones.copy()
        conexiones_caidas = []

        for ws in conexiones_activas:
            try:
                await ws.send_json(mensaje)
            except Exception:
                # La conexión falló, marcar para eliminar
                conexiones_caidas.append(ws)

        # Limpiar conexiones caídas
        for ws in conexiones_caidas:
            if ws in self.conexiones[id_asignacion]:
                self.conexiones[id_asignacion].remove(ws)

        # Si no quedan conexiones para esta asignación, limpiar el diccionario
        if not self.conexiones[id_asignacion]:
            del self.conexiones[id_asignacion]

    def obtener_estadisticas(self) -> dict:
        """Devuelve estadísticas de conexiones activas por asignación."""
        return {
            "total_asignaciones": len(self.conexiones),
            "conexiones_por_asignacion": {
                id_asignacion: len(conexiones)
                for id_asignacion, conexiones in self.conexiones.items()
            },
            "total_conexiones": sum(len(conexiones) for conexiones in self.conexiones.values())
        }

ws_manager = WebSocketManager()