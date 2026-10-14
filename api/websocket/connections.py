"""
api/websocket/connections.py
============================
Spec 004 FR-027, FR-028: the authenticated WebSockets of each account, so that a password change
or an administrative reset closes them at once instead of letting them live until they drop.

Process memory, like the rooms and the PvP lobby (AGENTS.md R18: one process). Sockets are held
weakly: one that ended without unregistering disappears with it.
"""

import asyncio
import logging
import weakref
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger("api.ws")

REVOKED_CODE = 4401  # application close code: credentials revoked

_by_user: dict[int, "weakref.WeakSet[WebSocket]"] = defaultdict(weakref.WeakSet)


def origin_allowed(websocket: WebSocket) -> bool:
    """Spec 004 FR-085 with decision N6: WebSockets keep connecting straight to the API (the
    frontend's proxy does not carry them), so a browser socket must come from an origin the API
    serves. Without `Origin` (other programs, tests) it is not a browser's and passes."""
    from api.config import settings

    origin = websocket.headers.get("origin")
    if origin is None:
        return True
    return origin.rstrip("/") in {allowed.rstrip("/") for allowed in settings.cors_origins}


def register(user_id: int, websocket: WebSocket) -> None:
    """Called on the event loop once a socket has authenticated."""
    _by_user[user_id].add(websocket)


def unregister(user_id: int, websocket: WebSocket) -> None:
    sockets = _by_user.get(user_id)
    if sockets is not None:
        sockets.discard(websocket)
        if not sockets:
            _by_user.pop(user_id, None)


async def close_user(user_id: int) -> int:
    """Close every socket of `user_id`; returns how many were open."""
    sockets = list(_by_user.pop(user_id, ()))
    for ws in sockets:
        try:
            await ws.close(code=REVOKED_CODE, reason="Sesión revocada.")
        except Exception as exc:  # already closing or gone: nothing left to revoke
            logger.debug("WS ya cerrado al revocar user=%s: %s", user_id, type(exc).__name__)
    if sockets:
        logger.info("WS revocados: user=%s conexiones=%d", user_id, len(sockets))
    return len(sockets)


def close_user_sync(user_id: int, timeout: float = 5.0) -> None:
    """From a `def` endpoint (threadpool): close the account's sockets on the server loop bound
    at startup, waiting up to `timeout` so the response comes after the sockets are closed."""
    from api.websocket.notifications import _server_loop

    if _server_loop is None or _server_loop.is_closed():
        return
    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        running = None
    if running is _server_loop:  # called on the loop itself: waiting here would deadlock
        _server_loop.create_task(close_user(user_id))
        return
    future = asyncio.run_coroutine_threadsafe(close_user(user_id), _server_loop)
    try:
        future.result(timeout=timeout)
    except Exception as exc:
        logger.warning("No se pudieron cerrar los WS de user=%s: %s", user_id, type(exc).__name__)
