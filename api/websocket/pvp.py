"""
api/websocket/pvp.py
====================
Liga PvP en tiempo real — carrera libre, ELO por resultado de partida.

Flujo:
  1. Cliente conecta → autentica con JWT en primer mensaje
  2. Entra a lobby del curso; si ya hay rival → crea partida
  3. Ambos reciben 10 ítems aleatorios del curso y responden a su ritmo
  4. Timer 180s: al expirar (o cuando ambos terminan) → se calcula ganador + ELO

Spec 007 delivery F (FR-040 … FR-042): the server fixes the end time once and sends it
(`ends_at`, `server_now`); equal scores are broken by total answer time (`match_outcome`); a
player whose socket drops keeps their place for `PVP_RECONNECT_GRACE_S` — a reconnect presenting
their `resume` token takes it back (4411 to the old socket), otherwise they lose by abandonment.
"""

import asyncio
import json
import logging
import random
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.websocket import connections
from api.websocket.limits import SocketLimits
from starlette.websockets import WebSocketState

from src.domain.elo.model import pvp_deltas
from src.domain.elo.ranks import rating_display, round_for_display
from src.domain.identity import ACCESS_EXPIRED_MESSAGE, public_name
from src.domain.pvp.outcome import match_outcome

logger = logging.getLogger("api.pvp")

pvp_router = APIRouter(prefix="/ws", tags=["pvp"])

MATCH_ITEMS = 10
MATCH_DURATION = 180  # segundos
# Spec 007 FR-061 (O-H2): after a failed close, wait this long before each of the 3 retries.
CLOSE_RETRY_DELAYS = (0.5, 1.0, 2.0)


# ── Estado en memoria por proceso ────────────────────────────────────────────

@dataclass
class LobbySlot:
    user_id: int
    name: str  # what the rival sees: the display name, else the username (spec 004 FR-021)
    elo: float  # expectation only: 1000 when unrated (FR-029a) — never shown
    ws: WebSocket
    shown_elo: int | None = None  # what the opponent sees; None = pending diagnostic
    # Señalización para el jugador en espera: el segundo en entrar setea match+event
    matched: asyncio.Event = field(default_factory=asyncio.Event)
    match: "ActiveMatch | None" = None
    course_id: str = ""
    # Spec 007 FR-042 (O-F1): the secret a reconnect of this player presents to take this place
    # back — sent with `waiting` and `game_start`, kept by the tab in sessionStorage.
    resume: str = field(default_factory=lambda: secrets.token_urlsafe(16))


@dataclass
class ActiveMatch:
    match_id: int
    course_id: str
    p1: LobbySlot
    p2: LobbySlot
    items: list[dict]          # sin correct_option
    correct: dict[str, str]    # item_id → correct_option
    score: dict[int, int] = field(default_factory=dict)
    answered: dict[int, set] = field(default_factory=dict)
    done: dict[int, bool] = field(default_factory=dict)
    finished: bool = False
    # Se activa cuando game_end ya salió hacia los dos: quien cierre en segundo lugar lo espera.
    closed: asyncio.Event = field(default_factory=asyncio.Event)
    # Spec 007 FR-040: fixed once when the match is formed. `started` and `ends_at_loop` are on
    # the server's monotonic clock (the event loop's); `ends_at` is the same instant in UTC.
    started: float | None = None
    ends_at_loop: float | None = None
    ends_at: str | None = None
    # FR-041 (O-F7): per player, the seconds from `started` to each correct answer, summed.
    elapsed: dict[int, float] = field(default_factory=dict)
    # FR-042: players whose socket dropped → the end of their grace; None = left after
    # answering every item (O-F4: no grace, no forfeit).
    away: dict[int, float | None] = field(default_factory=dict)
    grace_tasks: dict[int, asyncio.Task] = field(default_factory=dict)
    timer_task: asyncio.Task | None = None

    def all_done(self) -> bool:
        return self.done.get(self.p1.user_id) and self.done.get(self.p2.user_id)

    def slot_of(self, user_id: int) -> LobbySlot:
        return self.p1 if self.p1.user_id == user_id else self.p2

    def opponent_of(self, user_id: int) -> LobbySlot:
        return self.p2 if self.p1.user_id == user_id else self.p1


# ESTADO POR PROCESO — el despliegue debe ser de UN SOLO proceso (AGENTS.md R18).
# Con dos, cada uno tiene su propio lobby: dos jugadores del mismo curso conectados
# a procesos distintos nunca se emparejan, y sin ningún error visible.
# `settings.validate_runtime()` rechaza WEB_CONCURRENCY > 1 por esto.
# Las partidas sí quedan persistidas en `pvp_matches`; las que un reinicio deja
# huérfanas las cierra `expire_stale_pvp_matches()` al preparar el esquema.
_lobby: dict[str, LobbySlot] = {}  # course_id → LobbySlot en espera
_matches: dict[int, ActiveMatch] = {}  # match_id → ActiveMatch
_lock = asyncio.Lock()
# Spec 007 FR-050: the one live League socket of each student (any course, any phase).
_league_sockets: dict[int, WebSocket] = {}
# Spec 007 FR-042: the resume tokens of matches that are over → (user_id, when), so a late
# reconnect is told the match ended (4410) instead of entering as new. Kept ENDED_RESUME_TTL_S.
_ended_resumes: dict[str, tuple[int, float]] = {}
ENDED_RESUME_TTL_S = 600
# Background closes of replaced sockets (a half-open one may take the close timeout to answer).
_background: set[asyncio.Task] = set()

SECOND_TAB_CODE = 4409  # FR-050: the student already has the League open
TOO_MANY_MESSAGES_CODE = 4429  # FR-051: dropped frames kept coming
MATCH_ENDED_CODE = 4410  # FR-042: a resume names a match that is already over
RESUMED_ELSEWHERE_CODE = 4411  # FR-042: another socket of the student took the match over

# Survey 007 V22: how often the API closes orphaned matches (owner decision, 2026-10-20).
ORPHAN_SWEEP_EVERY_S = 300


async def sweep_orphaned_matches(repo, every_seconds: float = ORPHAN_SWEEP_EVERY_S) -> None:
    """Close orphaned matches periodically, for as long as the API runs (survey 007 V22).

    A match whose process died (a restart, a crash) stays `active`; bootstrap closes it only at
    the next deploy. `expire_stale_pvp_matches` closes those active for more than 600 s as
    `abandoned`, with no rating change; a real match lasts 180 s, so a live one is never
    touched. It runs in a thread (R17). A failed pass is logged and the sweep goes on. Stopping
    the API cancels this task only: it never closes a match.
    """
    while True:
        await asyncio.sleep(every_seconds)
        try:
            await asyncio.to_thread(repo.expire_stale_pvp_matches)
        except Exception as exc:
            logger.warning("PvP orphan sweep failed: %s", type(exc).__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _now() -> float:
    """The server's match clock: monotonic, the event loop's default clock (FR-040)."""
    return time.monotonic()


def _iso(moment: datetime) -> str:
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _utc_now() -> str:
    return _iso(datetime.now(timezone.utc))


def _grace_seconds() -> float:
    from api.config import settings

    return settings.pvp_reconnect_grace_s

class _TooManyMessages(Exception):
    """The socket kept sending frames that were dropped; it has been closed with 4429."""


def _socket_limits() -> SocketLimits:
    from api.config import settings

    return SocketLimits(
        max_frame_bytes=settings.pvp_max_frame_bytes,
        per_second=settings.pvp_max_messages_per_second,
        abuse_limit=settings.pvp_abuse_limit,
    )


async def _receive(ws: WebSocket, limits: SocketLimits) -> str:
    """The next frame the limits accept (spec 007 FR-051). A frame over the size or beyond the
    rate is dropped unparsed, with no reply; when drops persist the socket is closed with 4429."""
    while True:
        raw = await ws.receive_text()
        if limits.accept(len(raw.encode("utf-8"))):
            return raw
        if limits.abusive():
            try:
                await ws.close(code=TOO_MANY_MESSAGES_CODE, reason="Demasiados mensajes.")
            except Exception:
                pass
            raise _TooManyMessages()


async def _send(ws: WebSocket, msg: dict) -> bool:
    try:
        await ws.send_json(msg)
        return True
    except Exception as e:
        logger.warning("_send failed (%s): %s", msg.get("type"), e)
        return False


async def _send_to(match: ActiveMatch, user_id: int, msg: dict) -> bool:
    """Send to a player of the match; nothing to a player who is away (FR-042)."""
    if user_id in match.away:
        return False
    return await _send(match.slot_of(user_id).ws, msg)


async def _close_quietly(ws: WebSocket, code: int, reason: str) -> None:
    try:
        await ws.close(code=code, reason=reason)
    except Exception:
        pass


async def _course_rating(repo, user_id: int, course_id: str) -> float | None:
    """The player's derived course rating, None when unrated. Read in a thread, never under
    `_lock` (AGENTS R17)."""
    from src.application.services.rating_read_service import RatingReadService

    return await asyncio.to_thread(RatingReadService(repo).course_rating_of, user_id, course_id)


def _slot_ratings(course_rating: float | None) -> tuple[float, int | None]:
    """(expectation rating, shown rating): 1000 drives the expectation of an unrated player
    (FR-029a) but is never shown — the opponent sees None, i.e. pending diagnostic."""
    expectation = 1000.0 if course_rating is None else course_rating
    return expectation, rating_display(course_rating)["display_rating"]


def _game_end(
    my_score: int,
    opp_score: int,
    *,
    won: bool,
    draw: bool,
    applied: tuple,
    tiebreak: bool = False,
    forfeit: bool = False,
) -> dict:
    """One player's `game_end`: the applied delta and, for the screen, the number to show — half
    up on the value (spec 001 FR-028j), never rounded in the browser (survey 007 V14). Spec 007
    F: `tiebreak` when the time decided it (FR-041), `forfeit` when a player left (FR-042)."""
    delta, reason = applied
    return {
        "type": "game_end",
        "your_score": my_score,
        "opp_score": opp_score,
        "won": won,
        "draw": draw,
        "elo_delta": delta,
        "elo_delta_display": None if delta is None else round_for_display(delta),
        "elo_reason": reason,
        "tiebreak": tiebreak,
        "forfeit": forfeit,
    }


def _judge_answer(
    match: ActiveMatch, user_id: int, msg: dict, now: float | None = None
) -> tuple[str, bool] | None:
    """(item_id, is_correct) for an answer that counts; None for one to ignore: the match is over
    — closed, or read at or after the server's end time even before the timer has run (spec 007
    FR-040) — the item is not one of this match's or was already answered, or the choice is not
    text."""
    item_id, selected = msg.get("item_id"), msg.get("selected")
    if match.finished or not isinstance(item_id, str) or not isinstance(selected, str):
        return None
    if match.ends_at_loop is not None and (_now() if now is None else now) >= match.ends_at_loop:
        return None
    if item_id not in match.correct or item_id in match.answered[user_id]:
        return None
    return item_id, selected == match.correct[item_id]


async def _finish_match(
    match: ActiveMatch, repo, *, forfeit_by: int | None = None, abandon: str | None = None
) -> bool:
    """Close the match once: by score and time, as `forfeit_by`'s loss (FR-042, O-F2), or as
    abandoned with reason `abandon` and no rating change (O-F5; spec 004 FR-052 for an expired
    account). True when this call closed it, False when another close had started."""
    # Guard contra doble-cierre: ambos loops o el timer pueden disparar a la vez. Quien llega
    # segundo espera a que game_end haya salido: al volver, su loop termina y cierra el socket.
    async with _lock:
        already_closing = match.finished
        match.finished = True
    if already_closing:
        await match.closed.wait()
        return False
    try:
        if abandon is not None:
            await _abandon_match(match, repo, abandon)
        else:
            await _close_match(match, repo, forfeit_by)
    finally:
        match.closed.set()
        async with _lock:
            _matches.pop(match.match_id, None)
            _remember_ended(match)
    return True


def _remember_ended(match: ActiveMatch) -> None:
    """Keep the players' resume tokens of an ended match for a while (4410), pruning old ones.
    Called under `_lock`; no I/O."""
    now = _now()
    for token, (_, when) in list(_ended_resumes.items()):
        if now - when > ENDED_RESUME_TTL_S:
            del _ended_resumes[token]
    for slot in (match.p1, match.p2):
        _ended_resumes[slot.resume] = (slot.user_id, now)


async def _close_match(match: ActiveMatch, repo, forfeit_by: int | None = None) -> None:
    s1 = match.score.get(match.p1.user_id, 0)
    s2 = match.score.get(match.p2.user_id, 0)

    if forfeit_by is not None:
        # FR-042 (O-F2): a full loss for the player who left, whatever the score.
        outcome_p1 = 0.0 if forfeit_by == match.p1.user_id else 1.0
        tiebreak, reason = False, "forfeit"
    else:
        # FR-041: the score, then the total answer time in whole seconds (domain rule).
        e1 = match.elapsed.get(match.p1.user_id, 0.0)
        e2 = match.elapsed.get(match.p2.user_id, 0.0)
        outcome = match_outcome(s1, s2, e1, e2)
        outcome_p1, tiebreak, reason = outcome.result_p1, outcome.tiebreak, None
    if outcome_p1 == 1.0:
        winner_id = match.p1.user_id
    elif outcome_p1 == 0.0:
        winner_id = match.p2.user_id
    else:
        winner_id = None
    d1, d2 = pvp_deltas(match.p1.elo, match.p2.elo, outcome_p1)

    applied = await _persist_close(match, repo, winner_id, s1, s2, d1, d2, reason)
    # Report what was applied, never the computed delta (spec 001, FR-029c).
    if not applied:
        applied = {"p1": (0.0, "not_applied"), "p2": (0.0, "not_applied")}

    draw = winner_id is None
    won_p1, won_p2 = winner_id == match.p1.user_id, winner_id == match.p2.user_id
    flags = {"tiebreak": tiebreak, "forfeit": forfeit_by is not None}
    result_p1 = _game_end(s1, s2, won=won_p1, draw=draw, applied=applied["p1"], **flags)
    result_p2 = _game_end(s2, s1, won=won_p2, draw=draw, applied=applied["p2"], **flags)

    await asyncio.gather(
        _send_to(match, match.p1.user_id, result_p1),
        _send_to(match, match.p2.user_id, result_p2),
        return_exceptions=True,
    )


def players_in_play() -> set[int]:
    """Spec 004 FR-051: the accounts waiting in a lobby or playing a match in this process."""
    players = {slot.user_id for slot in list(_lobby.values())}
    for match in list(_matches.values()):
        players.update((match.p1.user_id, match.p2.user_id))
    return players


async def abandon_matches_of(user_id: int, repo, reason: str = "account_expired") -> int:
    """Spec 004 FR-051, FR-052: close every match of `user_id` still in play as abandoned.

    Each goes through `_finish_match`, so a match ends once: one whose close already started
    keeps that result, and this waits until both players have it. Returns how many matches this
    call abandoned.
    """
    async with _lock:
        mine = [m for m in _matches.values() if user_id in (m.p1.user_id, m.p2.user_id)]
    closed = await asyncio.gather(*(_finish_match(m, repo, abandon=reason) for m in mine))
    return sum(closed)


async def _abandon_match(match: ActiveMatch, repo, reason: str) -> None:
    """No rating moves for either player; the answers saved before stay. A player still
    connected is told why (spec 004 FR-052); one who is away gets nothing (spec 007 O-F5)."""
    try:
        await asyncio.to_thread(repo.abandon_pvp_match, match.match_id, reason)
    except Exception as e:
        # The row stays 'active' and `expire_stale_pvp_matches` closes it, also without rating.
        logger.error("abandon_pvp_match failed: %s", type(e).__name__)
    s1 = match.score.get(match.p1.user_id, 0)
    s2 = match.score.get(match.p2.user_id, 0)
    ends = [
        {"type": "game_end", "your_score": mine, "opp_score": theirs, "won": False,
         "draw": False, "abandoned": True, "reason": reason,
         "elo_delta": 0.0, "elo_reason": reason}
        for mine, theirs in ((s1, s2), (s2, s1))
    ]  # fmt: skip
    await asyncio.gather(
        _send_to(match, match.p1.user_id, ends[0]),
        _send_to(match, match.p2.user_id, ends[1]),
        return_exceptions=True,
    )


async def _persist_close(match, repo, winner_id, s1, s2, d1, d2, reason=None):
    """Spec 007 FR-061 (O-H2): persist the close — the first try and a retry after each of
    `CLOSE_RETRY_DELAYS`. If every try fails, the match is closed as abandoned `not_saved`, with
    no rating change, and None is returned (`game_end` then says `not_applied`). If even that
    write fails, the row stays active and the orphan sweep closes it later. `reason` is the
    outcome's reason where the delta is applied (F: 'forfeit', O-F3)."""
    for attempt, delay in enumerate((0.0, *CLOSE_RETRY_DELAYS)):
        if delay:
            await asyncio.sleep(delay)
        try:
            return await asyncio.to_thread(
                repo.finish_pvp_match,
                match_id=match.match_id,
                winner_id=winner_id,
                score_p1=s1, score_p2=s2,
                elo_delta_p1=d1, elo_delta_p2=d2,
                p1_id=match.p1.user_id, p2_id=match.p2.user_id,
                reason=reason,
            )
        except Exception as e:
            logger.error("finish_pvp_match try %d failed: %s", attempt + 1, type(e).__name__)
    try:
        await asyncio.to_thread(repo.abandon_pvp_match, match.match_id, "not_saved")
    except Exception as e:
        logger.error("abandon_pvp_match failed: %s", type(e).__name__)
    return None


async def _finish_early(match: ActiveMatch, timer_task: asyncio.Task | None, repo) -> None:
    """Both players answered everything. The timer is stopped only if it has not started closing
    the match: cancelled mid-close, it would drop game_end for both players."""
    if timer_task is not None and not match.finished:
        timer_task.cancel()
    await _finish_match(match, repo)


async def _timer(match: ActiveMatch, repo) -> None:
    """The one clock that ends the match: it sleeps until the server's end time (FR-040)."""
    if match.ends_at_loop is None:
        await asyncio.sleep(MATCH_DURATION)
    else:
        await asyncio.sleep(max(0.0, match.ends_at_loop - _now()))
    async with _lock:
        if match.match_id not in _matches:
            return
    await _finish_match(match, repo)


# ── Spec 007 FR-042: the grace, the forfeit and the resume ──────────────────


async def _player_left(match: ActiveMatch, user_id: int, websocket: WebSocket, repo) -> None:
    """The socket `websocket` of `user_id` ended while the match runs. Unless another socket took
    the place over, the player is away: a grace starts and the opponent is told — except for a
    player who had answered every item (O-F4). Bookkeeping under `_lock`, no I/O."""
    grace = _grace_seconds()
    async with _lock:
        if (
            match.finished
            or match.slot_of(user_id).ws is not websocket
            or user_id in match.away
        ):
            return
        if match.done.get(user_id):
            match.away[user_id] = None
            return
        match.away[user_id] = _now() + grace
        match.grace_tasks[user_id] = asyncio.create_task(_grace_end(match, user_id, repo, grace))
    logger.info("PvP away: user=%s match=%s grace=%ss", user_id, match.match_id, grace)
    await _send_to(
        match, match.opponent_of(user_id).user_id, {"type": "opponent_away", "grace_seconds": grace}
    )


async def _grace_end(match: ActiveMatch, user_id: int, repo, grace: float) -> None:
    """The grace is over: if the player has not come back, they lose by abandonment (O-F2); if
    the opponent is away too, the match is abandoned with no rating change (O-F5). The clock never
    waits for the grace (O-F6): a match that reached its end time is already closed."""
    await asyncio.sleep(grace)
    async with _lock:
        if match.finished or match.away.get(user_id) is None:
            return  # closed meanwhile, or the player came back
        match.grace_tasks.pop(user_id, None)
        other = match.opponent_of(user_id).user_id
        both_left = match.away.get(other) is not None
    if both_left:
        await _finish_match(match, repo, abandon="both_left")
    else:
        await _finish_match(match, repo, forfeit_by=user_id)


def _find_place(user_id: int, course_id: str, resume: str):
    """(slot, match) that `resume` names for this student in this course: a match still in
    memory, else their lobby slot (match None); None when it names neither. Under `_lock`."""
    def owns(slot: LobbySlot) -> bool:
        return slot.user_id == user_id and secrets.compare_digest(
            slot.resume.encode(), resume.encode()
        )

    for match in _matches.values():
        if match.course_id != course_id:
            continue
        for slot in (match.p1, match.p2):
            if owns(slot):
                return slot, match
    slot = _lobby.get(course_id)
    if slot is not None and owns(slot):
        return slot, None
    return None


async def _take_over(websocket: WebSocket, user_id: int, course_id: str, resume: str):
    """O-F1: bind `websocket` to the place `resume` names. Returns (slot, match, old socket,
    was away), "ended" when it names a match that is over, or None when it names nothing."""
    async with _lock:
        place = _find_place(user_id, course_id, resume)
        if place is None:
            ended = _ended_resumes.get(resume)
            return "ended" if ended is not None and ended[0] == user_id else None
        slot, match = place
        if match is not None and match.finished:
            return "ended"
        old, slot.ws = slot.ws, websocket
        was_away = False
        if match is not None:
            was_away = match.away.pop(user_id, None) is not None
            task = match.grace_tasks.pop(user_id, None)
            if task is not None:
                task.cancel()
        _league_sockets[user_id] = websocket
    return slot, match, old, was_away


async def _resume(
    websocket: WebSocket, repo, limits: SocketLimits, user_id: int, course_id: str, taken
) -> None:
    slot, match, old, was_away = taken
    connections.register(user_id, websocket)
    if old is not websocket:
        task = asyncio.create_task(
            _close_quietly(old, RESUMED_ELSEWHERE_CODE, "Tu partida siguió en otra conexión.")
        )
        _background.add(task)
        task.add_done_callback(_background.discard)
    if match is None:
        logger.info("PvP lobby resumed: user=%s course=%s", user_id, course_id)
        match, first_message = await _wait_for_match(websocket, slot, limits, course_id)
        if match is not None:
            await _answer_loop(websocket, repo, limits, user_id, match, first_message)
        return

    logger.info("PvP resumed: user=%s match=%s", user_id, match.match_id)
    opponent = match.opponent_of(user_id)
    await _send(websocket, {
        "type": "game_resume",
        "match_id": match.match_id,
        "items": match.items,
        "answered": [i["id"] for i in match.items if i["id"] in match.answered[user_id]],
        "your_score": match.score.get(user_id, 0),
        "opp_score": match.score.get(opponent.user_id, 0),
        "opponent": {"name": opponent.name, "elo": opponent.shown_elo},
        "duration_seconds": MATCH_DURATION,
        "ends_at": match.ends_at,
        "server_now": _utc_now(),
        "resume": slot.resume,
    })
    if was_away:
        await _send_to(match, opponent.user_id, {"type": "opponent_back"})
    await _answer_loop(websocket, repo, limits, user_id, match, None)


# ── Endpoint ─────────────────────────────────────────────────────────────────

@pvp_router.websocket("/pvp/{course_id}")
async def pvp_ws(websocket: WebSocket, course_id: str):
    from api.dependencies import authenticate_access_token, get_repository

    # Spec 004 FR-085 / N6: a browser socket only from an origin the API serves.
    if not connections.origin_allowed(websocket):
        await websocket.close(code=4003, reason="Origen no permitido.")
        return
    await websocket.accept()
    limits = _socket_limits()  # every frame of this socket, the token's included (FR-051)

    # 1. Autenticación
    try:
        raw = await asyncio.wait_for(_receive(websocket, limits), timeout=10.0)
        msg = json.loads(raw)
        repo = get_repository()
        # El repositorio es síncrono: cada llamada va a un hilo para no
        # bloquear el event loop y con él a todos los demás sockets.
        user = await asyncio.to_thread(
            authenticate_access_token, msg.get("token", ""), repo
        )
        if user["role"] != "student":
            raise ValueError("Solo estudiantes pueden entrar a PvP")
        user_id = user["user_id"]
        name = public_name(user.get("display_name"), user["username"])
        # get_user_enrollments returns each course under "id" (both repositories); reading
        # "course_id" raised KeyError and shut every enrolled student out (follow-up F-5).
        enrollments = {
            row["id"] for row in await asyncio.to_thread(repo.get_user_enrollments, user_id)
        }
        if course_id not in enrollments:
            raise ValueError("El estudiante no está inscrito en el curso")
    except _TooManyMessages:
        return
    except Exception as exc:
        try:
            if getattr(exc, "detail", None) == ACCESS_EXPIRED_MESSAGE:
                # Spec 004 FR-047: the screen shows why (P7).
                await websocket.close(
                    code=connections.EXPIRED_CODE, reason=connections.EXPIRED_REASON
                )
            else:
                await websocket.close(code=4001, reason="Auth failed")
        except Exception:
            pass
        logger.warning("PvP auth failed: %s", type(exc).__name__)
        return

    # Spec 007 FR-042 (O-F1): a reconnect presenting its resume token takes its place back —
    # in a match or in the lobby — before the one-socket rule; the old socket gets 4411.
    resume = msg.get("resume")
    if isinstance(resume, str) and resume:
        taken = await _take_over(websocket, user_id, course_id, resume)
        if taken == "ended":
            await _close_quietly(websocket, MATCH_ENDED_CODE, "La partida ya terminó.")
            return
        if taken is not None:
            try:
                await _resume(websocket, repo, limits, user_id, course_id, taken)
            finally:
                if _league_sockets.get(user_id) is websocket:
                    del _league_sockets[user_id]
            return

    # Spec 007 FR-050: one live League socket per student. No await between the check and the
    # claim, so two sockets of one student cannot both pass.
    current = _league_sockets.get(user_id)
    if current is not None and current.client_state == WebSocketState.CONNECTED:
        try:
            await websocket.close(
                code=SECOND_TAB_CODE, reason="Ya tienes la Liga abierta en otra pestaña."
            )
        except Exception:
            pass
        return
    _league_sockets[user_id] = websocket
    try:
        await _play(websocket, repo, limits, user_id, name, course_id)
    finally:
        if _league_sockets.get(user_id) is websocket:
            del _league_sockets[user_id]


async def _play(
    websocket: WebSocket, repo, limits: SocketLimits, user_id: int, name: str, course_id: str
) -> None:
    """The League socket of an authenticated, enrolled student: lobby, match and answers."""

    # Rating de la partida: el del curso (FR-026), leído fuera de _lock (AGENTS R17).
    # La expectativa usa 1000 si no hay rating; al rival se le muestra el valor o "pendiente".
    try:
        course_rating = await _course_rating(repo, user_id, course_id)
    except Exception:
        course_rating = None
    player_elo, shown_elo = _slot_ratings(course_rating)

    slot = LobbySlot(
        user_id=user_id, name=name, elo=player_elo, ws=websocket, shown_elo=shown_elo,
        course_id=course_id,
    )
    # Spec 004 FR-027: a password change or a reset closes this socket at once.
    connections.register(user_id, websocket)

    # El lock solo cubre el traspaso del lobby: nada de I/O dentro. Una
    # consulta a la DB con el lock tomado congela a todos los cursos a la vez.
    waiting: LobbySlot | None = None
    async with _lock:
        candidate = _lobby.get(course_id)
        # Descartar slot fantasma: si el que esperaba ya se desconectó, no emparejar
        if candidate and candidate.ws.client_state != WebSocketState.CONNECTED:
            del _lobby[course_id]
            candidate = None
        if candidate and candidate.user_id != user_id:
            # Emparejar — este jugador es el creador (p2). Sacarlo del lobby
            # aquí deja el emparejamiento decidido: nadie más puede tomarlo.
            del _lobby[course_id]
            waiting = candidate
        else:
            _lobby[course_id] = slot

    if waiting is None:
        match, first_message = await _wait_for_match(websocket, slot, limits, course_id)
        if match is not None:
            await _answer_loop(websocket, repo, limits, user_id, match, first_message)
        return

    match = await _form_match(websocket, repo, waiting, slot, course_id)
    if match is None:
        return
    await _start_match(match, repo)
    await _answer_loop(websocket, repo, limits, user_id, match, None)


async def _form_match(
    websocket: WebSocket, repo, waiting: LobbySlot, slot: LobbySlot, course_id: str
) -> ActiveMatch | None:
    """The creator (p2) forms the match with the waiting player (p1); None when it cannot (both
    sockets are closed)."""
    # Seleccionar ítems aleatorios — ya fuera del lock
    try:
        all_items = await asyncio.to_thread(
            repo.get_items_from_db, course_id=course_id
        )
    except Exception as e:
        logger.error("get_items_from_db: %s", e)
        all_items = []

    selected = random.sample(all_items, min(MATCH_ITEMS, len(all_items)))
    if not selected:
        # Sin ítems no hay partida: un 0-0 movería el ELO cuando las expectativas difieren.
        logger.warning("PvP: no items for course %s", course_id)
        for ws in (websocket, waiting.ws):
            try:
                await ws.close(code=4404, reason="No items")
            except Exception:
                pass
        return None
    item_ids = [i["id"] for i in selected]
    correct = {i["id"]: i["correct_option"] for i in selected}
    # No revelar correct_option al cliente (V2-R9)
    safe_items = [
        {"id": i["id"], "content": i["content"],
         "options": i["options"], "topic": i["topic"],
         "difficulty": i["difficulty"]}
        for i in selected
    ]

    try:
        match_id = await asyncio.to_thread(
            repo.create_pvp_match, course_id, waiting.user_id, slot.user_id, item_ids
        )
    except Exception as e:
        logger.error("create_pvp_match: %s", e)
        # El que esperaba ya salió del lobby: cerrar los dos sockets en
        # vez de dejarlo colgado hasta que expire su espera.
        await websocket.close(code=4500, reason="DB error")
        try:
            await waiting.ws.close(code=4500, reason="DB error")
        except Exception:
            pass
        return None

    # Spec 007 FR-040: the end time is fixed once, here, on the server.
    started = _now()
    match = ActiveMatch(
        match_id=match_id, course_id=course_id,
        p1=waiting, p2=slot,
        items=safe_items, correct=correct,
        score={waiting.user_id: 0, slot.user_id: 0},
        answered={waiting.user_id: set(), slot.user_id: set()},
        done={waiting.user_id: False, slot.user_id: False},
        started=started,
        ends_at_loop=started + MATCH_DURATION,
        ends_at=_iso(datetime.now(timezone.utc) + timedelta(seconds=MATCH_DURATION)),
        elapsed={waiting.user_id: 0.0, slot.user_id: 0.0},
    )
    async with _lock:
        _matches[match_id] = match
        waiting.match = match
    # Despertar al jugador en espera (instantáneo, sin sondeo)
    waiting.matched.set()
    return match


def _game_start(match: ActiveMatch, me: LobbySlot, opponent: LobbySlot) -> dict:
    return {
        "type": "game_start",
        "match_id": match.match_id,
        "items": match.items,
        "opponent": {"name": opponent.name, "elo": opponent.shown_elo},
        "duration_seconds": MATCH_DURATION,
        "ends_at": match.ends_at,
        "server_now": _utc_now(),
        "resume": me.resume,
    }


async def _start_match(match: ActiveMatch, repo) -> None:
    """Solo el creador (p2) emite game_start a ambos y arranca el ÚNICO cronómetro. A player whose
    game_start cannot be sent has dropped at the start: their grace runs from `started`."""
    sockets = (match.p1.ws, match.p2.ws)
    sent = await asyncio.gather(
        _send(sockets[0], _game_start(match, match.p1, match.p2)),
        _send(sockets[1], _game_start(match, match.p2, match.p1)),
    )
    match.timer_task = asyncio.create_task(_timer(match, repo))
    for slot, ws, ok in zip((match.p1, match.p2), sockets, sent):
        if not ok:
            await _player_left(match, slot.user_id, ws, repo)


async def _wait_for_match(
    websocket: WebSocket, slot: LobbySlot, limits: SocketLimits, course_id: str
) -> tuple[ActiveMatch | None, str | None]:
    """The waiting player: (match, an answer read while the wait was ending), or (None, None)
    when they left, timed out or another socket took their place (O-F1)."""
    first_message: str | None = None  # an answer read while the wait was ending (V10)
    # En espera — el creador setea slot.matched al emparejar.
    # Vigilamos el socket en PARALELO: si el jugador cierra la pestaña mientras
    # espera, receive_text() falla y lo sacamos del lobby (no queda fantasma).
    await _send(websocket, {"type": "waiting", "resume": slot.resume})
    matched_task = asyncio.ensure_future(slot.matched.wait())
    receive_task: asyncio.Future | None = None
    deadline = asyncio.get_running_loop().time() + 300.0
    while True:
        receive_task = asyncio.ensure_future(_receive(websocket, limits))
        remaining = deadline - asyncio.get_running_loop().time()
        await asyncio.wait(
            {matched_task, receive_task},
            timeout=max(remaining, 0.0),
            return_when=asyncio.FIRST_COMPLETED,
        )
        # Ask the task, not wait()'s result: the read can complete after wait() returned,
        # before this coroutine resumed (a loaded loop).
        if (
            receive_task.done()
            and not receive_task.cancelled()
            and receive_task.exception() is None
        ):
            # A message, not a closed tab (survey 007 V10). Once matched, it is this
            # player's first answer, sent right after game_start: keep it for the answer
            # loop. Before that it means nothing yet: ignore it and keep waiting.
            text = receive_task.result()
            if slot.matched.is_set():
                first_message = text
                receive_task = None
                break
            continue
        break
    # Drenar las tareas canceladas: si no esperamos la cancelación del
    # receive_text(), el canal de recepción queda ocupado y el loop de
    # respuestas falla con "cannot call recv while another coroutine is waiting".
    for t in (matched_task, receive_task):
        if t is None or t.done():
            continue
        t.cancel()
        try:
            await t
        except BaseException:
            pass
    # A player who leaves while waiting ends receive_text() with WebSocketDisconnect: read
    # it, or asyncio logs "Task exception was never retrieved" on every such exit (F-5).
    if receive_task is not None and receive_task.done() and not receive_task.cancelled():
        receive_task.exception()

    if slot.ws is not websocket:
        return None, None  # another socket of the student took this place (O-F1)
    if not slot.matched.is_set():
        # Desconexión o timeout → limpiar lobby y cerrar. The grace does not apply in the
        # lobby (FR-005): a waiting player who drops leaves the queue.
        async with _lock:
            if _lobby.get(course_id) is slot and slot.ws is websocket:
                del _lobby[course_id]
        try:
            await websocket.close()
        except Exception:
            pass
        return None, None
    return slot.match, first_message


async def _answer_loop(
    websocket: WebSocket,
    repo,
    limits: SocketLimits,
    user_id: int,
    match: ActiveMatch,
    first_message: str | None,
) -> None:
    """2. Loop de respuestas, until the match ends or the socket drops (then FR-042's grace)."""
    try:
        while True:
            if first_message is not None:
                raw, first_message = first_message, None
            else:
                raw = await _receive(websocket, limits)
            read_at = _now()
            try:
                msg = json.loads(raw)
            except ValueError:
                continue  # a malformed frame is ignored, like any message that is not an answer
            if not isinstance(msg, dict) or msg.get("type") != "answer":
                continue

            judged = _judge_answer(match, user_id, msg, read_at)
            if judged is None:
                continue  # ítem ajeno a la partida, ya respondido, o la partida terminó
            item_id, is_correct = judged
            match.answered[user_id].add(item_id)
            if is_correct:
                match.score[user_id] = match.score.get(user_id, 0) + 1
                if match.started is not None:  # FR-041 (O-F7): correct answers only
                    match.elapsed[user_id] = match.elapsed.get(user_id, 0.0) + (
                        read_at - match.started
                    )

            try:
                await asyncio.to_thread(
                    repo.save_pvp_answer, match.match_id, user_id, item_id, is_correct
                )
            except Exception as e:
                logger.warning("save_pvp_answer: %s", e)

            opponent = match.opponent_of(user_id)
            my_score = match.score[user_id]
            opp_score = match.score.get(opponent.user_id, 0)

            await _send(websocket, {
                "type": "answer_result",
                "item_id": item_id,
                "is_correct": is_correct,
                "your_score": my_score,
                "opp_score": opp_score,
            })
            await _send_to(match, opponent.user_id, {
                "type": "opponent_update",
                "opp_score": my_score,
            })

            # Marcar como terminado si respondió todos
            if len(match.answered[user_id]) >= len(match.items):
                match.done[user_id] = True

            if match.all_done():
                await _finish_early(match, match.timer_task, repo)
                break

    except _TooManyMessages:
        logger.info("PvP closed for too many messages: user=%s match=%s", user_id, match.match_id)
        await _player_left(match, user_id, websocket, repo)
    except WebSocketDisconnect:
        logger.info("PvP disconnect: user=%s match=%s", user_id, match.match_id)
        await _player_left(match, user_id, websocket, repo)
    except Exception as exc:
        logger.error("PvP loop error user=%s: %s", user_id, exc)
        await _player_left(match, user_id, websocket, repo)
