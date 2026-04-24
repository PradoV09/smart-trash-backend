"""Router para estado en vivo de asignaciones (admin only).

Endpoints:
- GET /admin/asignaciones/{id}/estado-vivo - Obtener estado actual
- WebSocket /ws/admin/asignacion/{id} - Conexión en tiempo real
"""

from fastapi import APIRouter, Depends, Query
from fastapi import WebSocket, WebSocketDisconnect
from core.dependecies import get_db, AdminDep
from core.response_builders import success_response
from core.security import verificar_token
from core.websocket_manager import ws_manager
from schemas.schema_responses import SuccessResponse
from schemas.schema_estado_vivo import EstadoVivoResponse
from controllers import controller_estado_vivo

# Router REST para estado vivo
router = APIRouter(prefix="/admin/asignaciones", tags=["Admin: Estado Vivo"])

router.get(
    "/{id_asignacion:int}/estado-vivo",
    response_model=SuccessResponse[EstadoVivoResponse]
)(controller_estado_vivo.obtener_estado_vivo)


# WebSocket para admin en tiempo real
@router.websocket("/ws/admin/asignacion/{id_asignacion}")
async def ws_estado_vivo_admin(
    websocket: WebSocket,
    id_asignacion: int,
    token: str = Query(...),
):
    """WebSocket para seguimiento en vivo de una asignación.
    
    Eventos emitidos cada 5 segundos:
    - posicion_actualizada: Nueva posición GPS
    - estado_cambio: Cambio de estado del recorrido
    - tripulacion_evento: Eventos de la tripulación
    """
    # Validar token JWT
    payload = verificar_token(token)
    if not payload:
        await websocket.close(code=1008)  # Policy violation
        return
    
    # Verificar que el usuario sea admin
    if payload.get("rol") != "admin":
        await websocket.close(code=1008)
        return

    await ws_manager.conectar(websocket, id_asignacion)
    
    try:
        # Mantener conexión viva y procesar mensajes
        while True:
            data = await websocket.receive_text()
            # El cliente puede enviar mensajes de control
            # Por ahora solo mantenemos la conexión viva
    except WebSocketDisconnect:
        ws_manager.desconectar(websocket, id_asignacion)