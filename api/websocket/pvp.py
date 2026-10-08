"""
api/websocket/pvp.py
====================
Liga PvP en tiempo real — carrera libre, ELO por resultado de partida.

Flujo:
  1. Cliente conecta → autentica con JWT en primer mensaje
  2. Entra a lobby del curso; si ya hay rival → crea partida
  3. Ambos reciben 10 ítems aleatorios del curso y responden a su ritmo
  4. Timer 180s: al expirar (o cuando ambos terminan) → se calcula ganador + ELO
"""

import asyncio
import json
import logging
import random
from dataclasses import dataclass, field

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from src.domain.elo.model import pvp_deltas
from src.domain.elo.ranks import rating_display

logger = logging.getLogger("api.pvp")

pvp_router = APIRouter(prefix="/ws", tags=["pvp"])

MATCH_ITEMS = 10
MATCH_DURATION = 180  # segundos


# ── Estado en memoria por proceso ────────────────────────────────────────────

@dataclass
class LobbySlot:
    user_id: int
    username: str
    elo: float  # expectation only: 1000 when unrated (FR-029a) — never shown
    ws: WebSocket
    shown_elo: int | None = None  # what the opponent sees; None = pending diagnostic
    # Señalización para el jugador en espera: el segundo en entrar setea match+event
    matched: asyncio.Event = field(default_factory=asyncio.Event)
    match: "ActiveMatch | None" = None


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

    def all_done(self) -> bool:
        return self.done.get(self.p1.user_id) and self.done.get(self.p2.user_id)


# ESTADO POR PROCESO — el despliegue debe ser de UN SOLO proceso (AGENTS.md R18).
# Con dos, cada uno tiene su propio lobby: dos jugadores del mismo curso conectados
# a procesos distintos nunca se emparejan, y sin ningún error visible.
# `settings.validate_runtime()` rechaza WEB_CONCURRENCY > 1 por esto.
# Las partidas sí quedan persistidas en `pvp_matches`; las que un reinicio deja
# huérfanas las cierra `expire_stale_pvp_matches()` al preparar el esquema.
_lobby: dict[str, LobbySlot] = {}  # course_id → LobbySlot en espera
_matches: dict[int, ActiveMatch] = {}  # match_id → ActiveMatch
_lock = asyncio.Lock()


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _send(ws: WebSocket, msg: dict) -> bool:
    try:
        await ws.send_json(msg)
        return True
    except Exception as e:
        logger.warning("_send failed (%s): %s", msg.get("type"), e)
        return False


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


async def _lobby_rating(repo, user_id: int, course_id: str) -> float:
    """The player's course rating for the match expectation (FR-026); 1000 when unrated."""
    rating = await _course_rating(repo, user_id, course_id)
    return 1000.0 if rating is None else rating


async def _finish_match(match: ActiveMatch, repo) -> None:
    # Guard contra doble-cierre: ambos loops o el timer pueden disparar a la vez
    async with _lock:
        if match.finished:
            return
        match.finished = True

    s1 = match.score.get(match.p1.user_id, 0)
    s2 = match.score.get(match.p2.user_id, 0)

    if s1 > s2:
        winner_id, outcome_p1 = match.p1.user_id, 1.0
    elif s2 > s1:
        winner_id, outcome_p1 = match.p2.user_id, 0.0
    else:
        winner_id, outcome_p1 = None, 0.5
    d1, d2 = pvp_deltas(match.p1.elo, match.p2.elo, outcome_p1)

    applied = None
    try:
        applied = await asyncio.to_thread(
            repo.finish_pvp_match,
            match_id=match.match_id,
            winner_id=winner_id,
            score_p1=s1, score_p2=s2,
            elo_delta_p1=d1, elo_delta_p2=d2,
            p1_id=match.p1.user_id, p2_id=match.p2.user_id,
        )
    except Exception as e:
        logger.error("finish_pvp_match error: %s", e)
    # Report what was applied, never the computed delta (spec 001, FR-029c).
    if not applied:
        applied = {"p1": (0.0, "not_applied"), "p2": (0.0, "not_applied")}

    result_p1 = {"type": "game_end", "your_score": s1, "opp_score": s2,
                 "won": winner_id == match.p1.user_id, "draw": winner_id is None,
                 "elo_delta": applied["p1"][0], "elo_reason": applied["p1"][1]}
    result_p2 = {"type": "game_end", "your_score": s2, "opp_score": s1,
                 "won": winner_id == match.p2.user_id, "draw": winner_id is None,
                 "elo_delta": applied["p2"][0], "elo_reason": applied["p2"][1]}

    await asyncio.gather(
        _send(match.p1.ws, result_p1),
        _send(match.p2.ws, result_p2),
        return_exceptions=True,
    )

    async with _lock:
        _matches.pop(match.match_id, None)


async def _timer(match: ActiveMatch, repo) -> None:
    await asyncio.sleep(MATCH_DURATION)
    async with _lock:
        if match.match_id not in _matches:
            return
    await _finish_match(match, repo)


# ── Endpoint ─────────────────────────────────────────────────────────────────

@pvp_router.websocket("/pvp/{course_id}")
async def pvp_ws(websocket: WebSocket, course_id: str):
    from api.dependencies import authenticate_access_token, get_repository

    await websocket.accept()

    # 1. Autenticación
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
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
        username = user["username"]
        # get_user_enrollments returns each course under "id" (both repositories); reading
        # "course_id" raised KeyError and shut every enrolled student out (follow-up F-5).
        enrollments = {
            row["id"] for row in await asyncio.to_thread(repo.get_user_enrollments, user_id)
        }
        if course_id not in enrollments:
            raise ValueError("El estudiante no está inscrito en el curso")
    except Exception as exc:
        await websocket.close(code=4001, reason="Auth failed")
        logger.warning("PvP auth failed: %s", exc)
        return

    # Rating de la partida: el del curso (FR-026), leído fuera de _lock (AGENTS R17).
    # La expectativa usa 1000 si no hay rating; al rival se le muestra el valor o "pendiente".
    try:
        course_rating = await _course_rating(repo, user_id, course_id)
    except Exception:
        course_rating = None
    player_elo, shown_elo = _slot_ratings(course_rating)

    slot = LobbySlot(
        user_id=user_id, username=username, elo=player_elo, ws=websocket, shown_elo=shown_elo
    )
    match: ActiveMatch | None = None
    is_creator = False  # True = segundo en entrar (emite game_start y arranca timer)

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
            is_creator = True
            waiting = candidate
        else:
            _lobby[course_id] = slot

    if waiting is not None:
        # Seleccionar ítems aleatorios — ya fuera del lock
        try:
            all_items = await asyncio.to_thread(
                repo.get_items_from_db, course_id=course_id
            )
        except Exception:
            all_items = []

        selected = random.sample(all_items, min(MATCH_ITEMS, len(all_items)))
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
                repo.create_pvp_match, course_id, waiting.user_id, user_id, item_ids
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
            return

        match = ActiveMatch(
            match_id=match_id, course_id=course_id,
            p1=waiting, p2=slot,
            items=safe_items, correct=correct,
            score={waiting.user_id: 0, user_id: 0},
            answered={waiting.user_id: set(), user_id: set()},
            done={waiting.user_id: False, user_id: False},
        )
        async with _lock:
            _matches[match_id] = match
        # Despertar al jugador en espera (instantáneo, sin sondeo)
        waiting.match = match
        waiting.matched.set()

    if match is None:
        # En espera — el creador setea slot.matched al emparejar.
        # Vigilamos el socket en PARALELO: si el jugador cierra la pestaña mientras
        # espera, receive_text() falla y lo sacamos del lobby (no queda fantasma).
        await _send(websocket, {"type": "waiting"})
        matched_task = asyncio.ensure_future(slot.matched.wait())
        disconnect_task = asyncio.ensure_future(websocket.receive_text())
        done, pending = await asyncio.wait(
            {matched_task, disconnect_task},
            timeout=300.0,
            return_when=asyncio.FIRST_COMPLETED,
        )
        # Drenar las tareas canceladas: si no esperamos la cancelación del
        # receive_text(), el canal de recepción queda ocupado y el loop de
        # respuestas falla con "cannot call recv while another coroutine is waiting".
        for t in pending:
            t.cancel()
            try:
                await t
            except BaseException:
                pass
        # A player who leaves while waiting ends receive_text() with WebSocketDisconnect: read
        # it, or asyncio logs "Task exception was never retrieved" on every such exit (F-5).
        for t in done:
            if not t.cancelled():
                t.exception()

        if matched_task not in done:
            # Desconexión o timeout → limpiar lobby y cerrar
            async with _lock:
                if _lobby.get(course_id) is slot:
                    del _lobby[course_id]
            try:
                await websocket.close()
            except Exception:
                pass
            return
        match = slot.match

    is_p1 = match.p1.user_id == user_id
    opponent = match.p2 if is_p1 else match.p1

    # Solo el creador (p2) emite game_start a ambos y arranca el ÚNICO cronómetro.
    # El jugador en espera entra directo a su loop de respuestas (su cliente ya
    # recibió game_start desde la coroutine del creador).
    timer_task: asyncio.Task | None = None
    if is_creator:
        await asyncio.gather(
            _send(match.p1.ws, {"type": "game_start", "match_id": match.match_id,
                                 "items": match.items,
                                 "opponent": {"username": match.p2.username, "elo": match.p2.shown_elo},
                                 "duration_seconds": MATCH_DURATION}),
            _send(match.p2.ws, {"type": "game_start", "match_id": match.match_id,
                                 "items": match.items,
                                 "opponent": {"username": match.p1.username, "elo": match.p1.shown_elo},
                                 "duration_seconds": MATCH_DURATION}),
        )
        timer_task = asyncio.create_task(_timer(match, repo))

    # 2. Loop de respuestas
    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            if msg.get("type") != "answer":
                continue

            item_id = msg.get("item_id", "")
            selected = msg.get("selected", "")

            if item_id in match.answered[user_id]:
                continue  # ya respondió este ítem

            is_correct = (selected == match.correct.get(item_id))
            match.answered[user_id].add(item_id)
            if is_correct:
                match.score[user_id] = match.score.get(user_id, 0) + 1

            try:
                await asyncio.to_thread(
                    repo.save_pvp_answer, match.match_id, user_id, item_id, is_correct
                )
            except Exception as e:
                logger.warning("save_pvp_answer: %s", e)

            my_score = match.score[user_id]
            opp_score = match.score.get(opponent.user_id, 0)

            await _send(websocket, {
                "type": "answer_result",
                "item_id": item_id,
                "is_correct": is_correct,
                "your_score": my_score,
                "opp_score": opp_score,
            })
            await _send(opponent.ws, {
                "type": "opponent_update",
                "opp_score": my_score,
            })

            # Marcar como terminado si respondió todos
            if len(match.answered[user_id]) >= len(match.items):
                match.done[user_id] = True

            if match.all_done():
                if timer_task:
                    timer_task.cancel()
                await _finish_match(match, repo)
                break

    except WebSocketDisconnect:
        logger.info("PvP disconnect: user=%s match=%s", user_id, match.match_id)
        # ponytail: NO cancelamos el timer aquí — si un jugador cae, el timer
        # (propiedad del creador) finaliza la partida a los 180s y el otro recibe
        # su resultado. El guard match.finished evita doble-cierre.
    except Exception as exc:
        logger.error("PvP loop error user=%s: %s", user_id, exc)
