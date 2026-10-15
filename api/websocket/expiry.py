"""
api/websocket/expiry.py
=======================
Spec 004 FR-047, FR-051: when an account's last day of access ends, its open connections end too.

HTTP requests and renewals check the last day on every call (`authenticate_access_token`); a
socket that authenticated before the day ended would live on, so a sweep closes it. Its PvP match,
if any, ends first as abandoned — no rating effect for either player, both told why — and only
then the socket closes (`pvp.abandon_matches_of`).

Process memory, like the sockets and the lobby (AGENTS.md R18: one process).
"""

import asyncio
import logging
from datetime import datetime, timezone

from api.websocket import connections, pvp
from api.websocket.connections import EXPIRED_CODE, EXPIRED_REASON
from src.domain.identity import access_expired

logger = logging.getLogger("api.ws")

__all__ = [
    "EXPIRED_CODE",
    "EXPIRED_REASON",
    "SWEEP_SECONDS",
    "run_sweeper",
    "sweep_expired_accounts",
]

SWEEP_SECONDS = 60


async def sweep_expired_accounts(repo, now: datetime | None = None) -> list[int]:
    """Close the sockets of every connected account past its last day, after abandoning its
    matches. Returns those accounts, in order. The repository is read in a thread (AGENTS R17)."""
    now = now or datetime.now(timezone.utc)
    candidates = set(connections.connected_user_ids()) | pvp.players_in_play()
    if not candidates:
        return []
    last_days = await asyncio.to_thread(repo.get_access_until_bulk, sorted(candidates))
    expired = sorted(u for u in candidates if access_expired(last_days.get(u), now))
    for user_id in expired:
        await pvp.abandon_matches_of(user_id, repo)
        await connections.close_user(user_id, EXPIRED_CODE, EXPIRED_REASON)
    if expired:
        logger.info("Cuentas vencidas desconectadas: %d", len(expired))
    return expired


async def run_sweeper(get_repo, interval: float = SWEEP_SECONDS) -> None:
    """Started with the app: one sweep per `interval` seconds until cancelled at shutdown. A sweep
    that fails is logged and the next one tries again."""
    while True:
        await asyncio.sleep(interval)
        try:
            await sweep_expired_accounts(get_repo())
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("Barrido de cuentas vencidas falló: %s", type(exc).__name__)
