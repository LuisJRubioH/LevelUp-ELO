"""
api/websocket/notifications.py
================================
WebSocket para notificaciones en tiempo real.

Eventos emitidos:
  procedure_submitted  → docente ve badge actualizado al subir procedimiento
  procedure_graded     → estudiante recibe notificación al calificar docente
  new_group_member     → docente ve estudiante unido al grupo

Uso en FastAPI (en main.py):
    from api.websocket.notifications import ws_router, notify
    app.include_router(ws_router)

Desde cualquier endpoint:
    await notify(room=f"teacher_{teacher_id}", event="procedure_submitted", data={...})
"""

import asyncio
import json
import logging
from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("api.ws")

ws_router = APIRouter(prefix="/ws", tags=["websocket"])

# ── Mapa de conexiones activas por sala ───────────────────────────────────────
# ESTADO POR PROCESO — tener los sockets locales es correcto, pero `notify()`
# solo alcanza a los de ESTE proceso. Con varios workers un evento llega a unos
# clientes y a otros no. Ver AGENTS.md R18: el despliegue es de un solo proceso.
# room → set de WebSocket activos
_rooms: dict[str, set[WebSocket]] = defaultdict(set)
_lock = asyncio.Lock()

# Loop del servidor, registrado al arrancar. Los endpoints `def` de FastAPI
# corren en un hilo del threadpool, donde no hay loop que descubrir.
_server_loop: asyncio.AbstractEventLoop | None = None


def bind_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Registra el event loop del servidor para notify_sync()."""
    global _server_loop
    _server_loop = loop


# ── Endpoints ─────────────────────────────────────────────────────────────────


@ws_router.websocket("/notifications/{room}")
async def websocket_notifications(websocket: WebSocket, room: str):
    """
    Conecta a una sala de notificaciones.

    Salas convencionales:
      - "teacher_{id}"   → panel del docente
      - "student_{id}"   → panel del estudiante
      - "group_{id}"     → sala de un grupo

    El cliente debe enviar el JWT como primer mensaje para autenticarse:
        { "token": "<access_token>" }
    Luego permanece a la escucha de eventos JSON.
    """
    await websocket.accept()

    # Autenticación básica por token en primer mensaje
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        msg = json.loads(raw)
        token = msg.get("token", "")
        if not token:
            await websocket.close(code=4001, reason="Token requerido.")
            return

        from api.dependencies import authenticate_access_token, get_repository

        repo = get_repository()
        user = authenticate_access_token(token, repo)
        user_id = user["user_id"]
        allowed = user["role"] == "admin"
        if room.startswith("student_"):
            allowed = allowed or (user["role"] == "student" and room == f"student_{user_id}")
        elif room.startswith("teacher_"):
            allowed = allowed or (user["role"] == "teacher" and room == f"teacher_{user_id}")
        elif room.startswith("group_"):
            group_id = int(room.removeprefix("group_"))
            profile = repo.get_user_by_id(user_id)
            teacher_groups = (
                {g["group_id"] for g in repo.get_groups_by_teacher(user_id)}
                if user["role"] == "teacher" else set()
            )
            allowed = allowed or profile.get("group_id") == group_id or group_id in teacher_groups
        if not allowed:
            await websocket.close(code=4003, reason="Sala no autorizada.")
            return
        logger.info("WS conectado: user=%s sala=%s", user_id, room)
    except asyncio.TimeoutError:
        await websocket.close(code=4002, reason="Timeout de autenticación.")
        return
    except Exception as exc:
        logger.warning("WS auth fallida sala=%s: %s", room, exc)
        await websocket.close(code=4003, reason="Token inválido.")
        return

    async with _lock:
        _rooms[room].add(websocket)

    try:
        await websocket.send_json({"type": "connected", "room": room})
        # Mantener conexión viva con ping cada 30s
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        logger.info("WS desconectado: user=%s sala=%s", user_id, room)
    except Exception as exc:
        logger.warning("WS error sala=%s: %s", room, exc)
    finally:
        async with _lock:
            _rooms[room].discard(websocket)
            if not _rooms[room]:
                del _rooms[room]


# ── API de notificación interna ───────────────────────────────────────────────


async def notify(room: str, event: str, data: dict) -> int:
    """
    Envía un evento a todos los WebSocket conectados en una sala.

    Retorna el número de clientes que recibieron el mensaje.
    """
    payload = json.dumps({"type": event, **data})
    sent = 0
    dead: list[WebSocket] = []

    async with _lock:
        sockets = list(_rooms.get(room, set()))

    for ws in sockets:
        try:
            await ws.send_text(payload)
            sent += 1
        except Exception:
            dead.append(ws)

    # Limpiar sockets muertos
    if dead:
        async with _lock:
            for ws in dead:
                _rooms[room].discard(ws)

    return sent


def notify_sync(room: str, event: str, data: dict) -> None:
    """Programa una notificación desde un endpoint síncrono.

    Buscar el loop desde aquí no funcionaba: FastAPI corre los endpoints
    `def` en un hilo del threadpool, donde no hay ninguno, así que el aviso
    se perdía en silencio. Se usa el loop registrado al arrancar.
    """
    loop = _server_loop
    if loop is None or loop.is_closed():
        logger.warning(
            "Notificación '%s' descartada: no hay event loop registrado (sala=%s)",
            event,
            room,
        )
        return
    asyncio.run_coroutine_threadsafe(notify(room, event, data), loop)
