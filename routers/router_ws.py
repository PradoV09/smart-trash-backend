# routers/router_ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, status
from core.websocket_manager import ws_manager
from core.security import verificar_token
from services.service_asignacionrutas import AsignacionService
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSockets"])

@router.get("/stats")
async def obtener_estadisticas_ws():
    """Obtiene estadísticas de conexiones WebSocket activas."""
    return ws_manager.obtener_estadisticas()

@router.websocket("/asignacion/{id_asignacion}")
async def ws_asignacion(
    websocket: WebSocket,
    id_asignacion: int,
    token: str = Query(...),  # ?token=eyJ...
):
    logger.info(f"[ASIGNACION {id_asignacion}] Intento de conexión WebSocket")
    
    # 1. Validar token (rápido, sin operaciones bloqueantes)
    payload = verificar_token(token)
    if not payload:
        logger.error(f"[ASIGNACION {id_asignacion}] Token inválido: {token[:50]}...")
        await websocket.close(code=1008, reason="Token inválido")
        return
    
    user_id = payload.get("sub")
    username = payload.get("username")
    logger.info(f"[ASIGNACION {id_asignacion}] Token válido para usuario {username} (ID: {user_id})")
    
    # 2. Verificar que el usuario tiene permiso para esta asignación
    try:
        from database import SessionLocal
        async with SessionLocal() as db:
            asignacion_service = AsignacionService(db)
            tiene_permiso = await asignacion_service.verificar_permiso_usuario(user_id, id_asignacion)
            if not tiene_permiso:
                logger.error(f"[ASIGNACION {id_asignacion}] Usuario {user_id} no tiene permiso")
                await websocket.close(code=1008, reason="Sin permiso")
                return
    except Exception as e:
        logger.error(f"[ASIGNACION {id_asignacion}] Error verificando permisos: {e}")
        await websocket.close(code=1011, reason="Error interno")
        return
    
    # 3. Aceptar la conexión
    await websocket.accept()
    logger.info(f"[ASIGNACION {id_asignacion}] Conexión aceptada para usuario {username}")
    
    # 4. Variables de control
    ping_task = None
    client_disconnected = False
    
    async def send_ping():
        """Enviar ping cada 30 segundos para mantener la conexión viva"""
        nonlocal client_disconnected
        while not client_disconnected:
            try:
                await asyncio.sleep(30)
                if websocket.client_state.name == "CONNECTED":
                    ping_message = {
                        "type": "ping", 
                        "timestamp": asyncio.get_event_loop().time(),
                        "asignacion_id": id_asignacion
                    }
                    await websocket.send_text(json.dumps(ping_message))
                    logger.debug(f"[ASIGNACION {id_asignacion}] Ping enviado")
            except Exception as e:
                logger.warning(f"[ASIGNACION {id_asignacion}] Error enviando ping: {e}")
                break
    
    # Iniciar tarea de ping
    ping_task = asyncio.create_task(send_ping())
    
    try:
        # 5. Bucle principal de recepción de mensajes
        while True:
            try:
                # Esperar mensajes del cliente con timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60)
                logger.info(f"[ASIGNACION {id_asignacion}] Mensaje recibido: {data[:200]}")
                
                # Procesar mensaje
                try:
                    message = json.loads(data)
                    message_type = message.get("type", "unknown")
                    
                    if message_type == "pong":
                        logger.debug(f"[ASIGNACION {id_asignacion}] Pong recibido")
                        continue
                    elif message_type == "status_update":
                        # Procesar actualización de estado
                        await process_status_update(id_asignacion, message)
                        # Responder confirmación
                        await websocket.send_text(json.dumps({
                            "type": "ack",
                            "message_id": message.get("id"),
                            "status": "received",
                            "asignacion_id": id_asignacion
                        }))
                    else:
                        logger.warning(f"[ASIGNACION {id_asignacion}] Tipo de mensaje desconocido: {message_type}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"[ASIGNACION {id_asignacion}] Mensaje no es JSON válido: {data[:100]}")
                    
            except asyncio.TimeoutError:
                # Timeout en recepción - la conexión sigue viva
                logger.debug(f"[ASIGNACION {id_asignacion}] Timeout esperando mensaje, enviando ping de cortesía...")
                try:
                    await websocket.send_text(json.dumps({
                        "type": "ping", 
                        "timestamp": asyncio.get_event_loop().time(),
                        "asignacion_id": id_asignacion
                    }))
                except Exception as e:
                    logger.warning(f"[ASIGNACION {id_asignacion}] Error enviando ping de cortesía: {e}")
                continue
                
    except WebSocketDisconnect:
        logger.info(f"[ASIGNACION {id_asignacion}] Cliente desconectado (cierre normal)")
        client_disconnected = True
        
    except Exception as e:
        logger.error(f"[ASIGNACION {id_asignacion}] Error inesperado: {type(e).__name__}: {e}")
        client_disconnected = True
        
    finally:
        # Limpiar tarea de ping
        if ping_task:
            ping_task.cancel()
            try:
                await ping_task
            except asyncio.CancelledError:
                pass
        
        # Desconectar del manager
        ws_manager.desconectar(websocket, id_asignacion)
        
        # Cerrar conexión si aún está abierta
        try:
            await websocket.close()
            logger.info(f"[ASIGNACION {id_asignacion}] Conexión cerrada correctamente")
        except:
            pass

async def process_status_update(asignacion_id: int, message: dict):
    """Procesa actualizaciones de estado recibidas por WebSocket"""
    try:
        # Aquí puedes implementar la lógica para procesar actualizaciones de estado
        # Por ejemplo, actualizar el estado de la asignación en la base de datos
        nuevo_estado = message.get("estado")
        if nuevo_estado:
            logger.info(f"[ASIGNACION {asignacion_id}] Actualizando estado a: {nuevo_estado}")
            
            # Crear sesión de base de datos para la actualización
            from database import SessionLocal
            async with SessionLocal() as db:
                asignacion_service = AsignacionService(db)
                # Implementar lógica de actualización aquí
                # await asignacion_service.actualizar_estado(asignacion_id, nuevo_estado)
            
            # Notificar a otros clientes conectados
            await ws_manager.emitir_cambio_estado(
                asignacion_id, 
                message.get("estado_anterior", "desconocido"),
                nuevo_estado
            )
    except Exception as e:
        logger.error(f"[ASIGNACION {asignacion_id}] Error procesando actualización: {e}")

@router.websocket("/public/asignacion/{id_asignacion}")
async def ws_asignacion_publica(
    websocket: WebSocket,
    id_asignacion: int,
):
    """WebSocket público para recibir actualizaciones de posición GPS sin requerir token."""
    await ws_manager.conectar(websocket, id_asignacion)
    try:
        while True:
            await websocket.receive_text()  # Mantiene la conexión viva
    except WebSocketDisconnect:
        ws_manager.desconectar(websocket, id_asignacion)