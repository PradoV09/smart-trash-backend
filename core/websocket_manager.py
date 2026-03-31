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
        self.conexiones[id_asignacion].remove(websocket)
        if not self.conexiones[id_asignacion]:
            del self.conexiones[id_asignacion]

    async def broadcast(self, id_asignacion: int, mensaje: dict):
        """Envía un mensaje JSON a todos los clientes conectados a una asignación."""
        conexiones = self.conexiones.get(id_asignacion, [])
        caidas = []
        for ws in conexiones:
            try:
                await ws.send_json(mensaje)
            except Exception:
                caidas.append(ws)
        for ws in caidas:
            self.conexiones[id_asignacion].remove(ws)

ws_manager = WebSocketManager()