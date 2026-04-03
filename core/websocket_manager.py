# core/websocket_manager.py

"""Administrador simple de conexiones WebSocket agrupadas por asignación.

Permite que varios clientes se suscriban al estado de una misma asignación
para recibir eventos en tiempo real cuando el recorrido cambia de estado.
"""

from fastapi import WebSocket
from typing import DefaultDict
from collections import defaultdict

class WebSocketManager:

    def __init__(self):
        # agrupa conexiones por id_asignacion
        self.conexiones: DefaultDict[int, list[WebSocket]] = defaultdict(list)

    async def conectar(self, websocket: WebSocket, id_asignacion: int):
        """Acepta una conexión nueva y la asocia al grupo de una asignación."""
        await websocket.accept()
        self.conexiones[id_asignacion].append(websocket)

    def desconectar(self, websocket: WebSocket, id_asignacion: int):
        """Remueve una conexión cuando el cliente se desconecta."""
        if id_asignacion in self.conexiones and websocket in self.conexiones[id_asignacion]:
            self.conexiones[id_asignacion].remove(websocket)

            # Si no quedan conexiones para esta asignación, limpiar el diccionario
            if not self.conexiones[id_asignacion]:
                del self.conexiones[id_asignacion]

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