"""
api/websocket/connections.py
============================
Spec 004 FR-027, FR-028: the authenticated WebSockets of each account, so that a password change
or an administrative reset closes them at once instead of letting them live until they drop; and
FR-047: so that the end of an account's last day of access closes them too (`expiry.py`).

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
EXPIRED_CODE = 4403  # application close code: the account's last day of access is over (E3)
# A close reason holds at most 123 bytes: the screen shows the owner's full message (P7).
EXPIRED_REASON = "Acceso vencido."

_by_user: dict[int, "weakref.WeakSet[WebSocket]"] = defaultdict(weakref.WeakSet)


def register(user_id: int, websocket: WebSocket) -> None:
    """Called on the event loop once a socket has authenticated."""
    _by_user[user_id].add(websocket)


def unregister(user_id: int, websocket: WebSocket) -> None:
    sockets = _by_user.get(user_id)
    if sockets is not None:
        sockets.discard(websocket)
        if not sockets:
            _by_user.pop(user_id, None)


def connected_user_ids() -> list[int]:
    """The accounts with at least one authenticated socket open in this process."""
    return [user_id for user_id, sockets in list(_by_user.items()) if len(sockets)]


async def close_user(
    user_id: int, code: int = REVOKED_CODE, reason: str = "Sesión revocada."
) -> int:
    """Close every socket of `user_id`; returns how many were open."""
    sockets = list(_by_user.pop(user_id, ()))
    for ws in sockets:
        try:
            await ws.close(code=code, reason=reason)
        except Exception as exc:  # already closing or gone: nothing left to revoke
            logger.debug("WS ya cerrado al revocar user=%s: %s", user_id, type(exc).__name__)
    if sockets:
        logger.info("WS cerrados (%s): user=%s conexiones=%d", code, user_id, len(sockets))
    return len(sockets)


def close_user_sync(
    user_id: int,
    timeout: float = 5.0,
    code: int = REVOKED_CODE,
    reason: str = "Sesión revocada.",
) -> None:
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
        _server_loop.create_task(close_user(user_id, code, reason))
        return
    future = asyncio.run_coroutine_threadsafe(close_user(user_id, code, reason), _server_loop)
    try:
        future.result(timeout=timeout)
    except Exception as exc:
        logger.warning("No se pudieron cerrar los WS de user=%s: %s", user_id, type(exc).__name__)
