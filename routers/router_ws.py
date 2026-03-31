# routers/router_ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.websocket_manager import ws_manager
from core.security import verificar_token

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/asignacion/{id_asignacion}")
async def ws_asignacion(
    websocket: WebSocket,
    id_asignacion: int,
    token: str = Query(...),  # ?token=eyJ...
):
    # validar token antes de aceptar la conexión
    payload = verificar_token(token)
    if not payload:
        await websocket.close(code=1008)  # 1008 = policy violation
        return

    await ws_manager.conectar(websocket, id_asignacion)
    try:
        while True:
            await websocket.receive_text()  # mantiene la conexión viva
    except WebSocketDisconnect:
        ws_manager.desconectar(websocket, id_asignacion)