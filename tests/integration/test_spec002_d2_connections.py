"""
Spec 002 delivery D2 (tasks T002–T008): connections and the event loop.

- A read on the student's hot paths costs one round trip on PostgreSQL: no `BEGIN`/`ROLLBACK`
  around it (FR-025, SC-003), and it writes nothing (the decorator is only on reads).
- A connection the server closed is replaced before a request uses it (FR-023).
- Idle connections up to DB_POOL_MIN_IDLE survive a burst; never more than 5 (FR-020, FR-022).
- A slow repository call, or a wait for the pool, inside an asynchronous handler does not stop
  other requests (FR-024, SC-004).
"""

import asyncio
import os
import threading
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit

import psycopg2
import pytest

from tests.integration.conftest import make_student, sql
from tests.integration.pg_message_proxy import MessageProxy
from tests.integration.statement_recorder import record_statements

_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")
_SSLMODE = os.environ.get("DATABASE_SSLMODE", "disable")

# The reads behind /next-question, /stats, the course map, the lesson, the ranking and the
# course list (owner decision N2, 2026-10-19), measured by calling those endpoints.
HOT_READS = {
    "get_answered_item_ids": lambda uid: (uid,),
    "get_course_topic_ratings": lambda uid: (uid, "algebra_basica"),
    "get_course_topic_ratings_bulk": lambda uid: ([uid], "algebra_basica"),
    "get_items_from_db": lambda uid: (None, "geometria"),
    "get_user_by_id": lambda uid: (uid,),
    "get_user_enrollments": lambda uid: (uid,),
    "get_courses": lambda uid: (),
    "get_current_context_course_ids_bulk": lambda uid: ([uid],),
    "get_study_streak": lambda uid: (uid,),
    "get_total_attempts_count": lambda uid: (uid,),
    "get_diagnostic": lambda uid: (uid, "algebra_basica"),
    "get_lesson_states": lambda uid: (uid, "algebra_basica"),
    "get_lesson_progress": lambda uid: (uid, "algebra_basica", "D2-NODE"),
    "get_lesson_interactions": lambda uid: (uid, "algebra_basica", "D2-NODE"),
    # Spec 003 L4: every lesson load reads the stored outcome; the summary reads the history.
    "get_lesson_outcomes": lambda uid: (uid, "algebra_basica"),
    "get_lesson_answers": lambda uid: (uid, "algebra_basica"),
    "get_ranking_participants": lambda uid: ("global",),
    "get_available_courses_by_level": lambda uid: ("colegio",),
    "get_completed_diagnostic_course_ids": lambda uid: (uid,),
    "get_education_level": lambda uid: (uid,),
    # Spec 008 FR-042: /stats reads the student's results per subtopic.
    "get_subtopic_attempts": lambda uid: (uid,),
    # Spec 007 M (FR-031, FR-032): a League match reads the pair's day and the items seen.
    "get_pvp_pair_matches_since": lambda uid: (uid, uid, datetime.now(timezone.utc)),
    "get_item_ids_seen_since": lambda uid: ([uid], "algebra_basica", datetime.now(timezone.utc)),
}


@pytest.fixture
def postgres_repo(_postgres_repo):
    return _postgres_repo


def _new_repo(monkeypatch, url, **env):
    """A second PostgreSQL repository on `url`, without bootstrap (the session's is migrated)."""
    from src.infrastructure.persistence.postgres_repository import PostgresRepository

    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("DATABASE_SSLMODE", _SSLMODE)
    monkeypatch.setenv("RUN_MIGRATIONS", "0")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return PostgresRepository()


# ── FR-025: one round trip per read ─────────────────────────────────────────


def test_spec002_d2_a_read_costs_one_round_trip(postgres_repo, monkeypatch):
    """US5-AS1, FR-025, SC-003: each hot read sends exactly its own statements — no BEGIN, no
    ROLLBACK."""
    uid = make_student(postgres_repo)
    target = urlsplit(_PG_URL)
    with MessageProxy(target.hostname, target.port or 5432) as proxy:
        repo = _new_repo(monkeypatch, proxy.url_for(_PG_URL))
        try:
            recorded = record_statements(monkeypatch, type(repo))
            extra = {}
            for name, args in HOT_READS.items():
                proxy.queries.clear()
                recorded.statements.clear()
                getattr(repo, name)(*args(uid))
                time.sleep(0.05)  # the proxy thread forwards asynchronously
                if len(proxy.queries) != len(recorded.statements):
                    extra[name] = [q.split()[0] for q in proxy.queries]
            assert extra == {}, f"round trips beyond the method's own statements: {extra}"
        finally:
            repo._pool.closeall()


@pytest.mark.parametrize("engine", ["sqlite", "postgres"])
def test_spec002_d2_read_only_methods_write_nothing(engine):
    """FR-025: the decorator is on exactly the hot reads, on both engines, and none of them
    writes, locks or commits."""
    import inspect
    import re

    if engine == "sqlite":
        from src.infrastructure.persistence.sqlite_repository import SQLiteRepository as cls
    else:
        from src.infrastructure.persistence.postgres_repository import PostgresRepository as cls

    decorated = {
        name
        for name, fn in inspect.getmembers(cls, inspect.isfunction)
        if getattr(fn, "_read_only", False)
    }
    assert decorated == set(HOT_READS)
    forbidden = re.compile(r"\b(INSERT|UPDATE|DELETE|FOR\s+UPDATE)\b|\.commit\(")
    for name in decorated:
        source = inspect.getsource(getattr(cls, name))
        assert not forbidden.search(source), f"{cls.__name__}.{name} writes"


# ── FR-023: a closed connection is replaced ─────────────────────────────────


def _terminate_backends(repo):
    """Ends, from another session, every idle backend the repository's pool holds."""
    pids = []
    for conn in list(repo._pool._pool):
        pids.append(conn.get_backend_pid())
    admin = psycopg2.connect(_PG_URL, sslmode=_SSLMODE)
    admin.autocommit = True
    with admin.cursor() as cur:
        for pid in pids:
            cur.execute("SELECT pg_terminate_backend(%s)", (pid,))
    admin.close()
    time.sleep(0.2)
    return pids


def test_spec002_d2_a_closed_connection_is_replaced(postgres_repo, monkeypatch):
    """US5-AS2, FR-023: after the server closes the pooled connections, a read and a write both
    succeed (the read retries once on a fresh connection; the checkout probes a connection idle
    past DB_POOL_PROBE_AFTER_S)."""
    uid = make_student(postgres_repo)
    repo = _new_repo(monkeypatch, _PG_URL, DB_POOL_PROBE_AFTER_S="0")
    try:
        assert repo.get_user_by_id(uid)
        assert _terminate_backends(repo)
        assert repo.get_user_by_id(uid)["id"] == uid

        _terminate_backends(repo)
        repo.record_lesson_event(uid, "algebra_basica", "D2-NODE", "node_opened")
    finally:
        repo._pool.closeall()


# ── FR-022: idle connections survive a burst ────────────────────────────────


def test_spec002_d2_idle_connections_survive_a_burst(postgres_repo, monkeypatch):
    """US5-AS3, FR-020, FR-022: five concurrent checkouts, then DB_POOL_MIN_IDLE (default 2)
    connections stay open, never more than five in all."""
    monkeypatch.delenv("DB_POOL_MIN_IDLE", raising=False)
    repo = _new_repo(monkeypatch, _PG_URL)
    try:
        held = [repo.get_connection() for _ in range(5)]
        assert len(repo._pool._used) == 5
        with pytest.raises(psycopg2.pool.PoolError):
            repo._pool.getconn()  # the sixth is refused: maxconn stays 5
        for conn in held:
            repo.put_connection(conn)
        idle = [c for c in repo._pool._pool if not c.closed]
        assert len(idle) == 2
    finally:
        repo._pool.closeall()


# ── FR-024: the event loop is never blocked ─────────────────────────────────


async def _health_while(client_call, app):
    """Starts `client_call` and measures GET / while it runs."""
    import httpx

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="https://d2.local") as client:
        slow = asyncio.create_task(client_call(client))
        # Timed from here: a blocked loop delays the sleep itself, not only the request.
        started = time.monotonic()
        await asyncio.sleep(0.3)
        response = await client.get("/")  # no database: only the loop can delay it
        elapsed = time.monotonic() - started - 0.3
        slow_response = await slow
        # The slow call reached the repository (the item does not exist): it was not refused
        # earlier, so its wait really overlapped GET /.
        assert slow_response.status_code == 404, slow_response.text
        return response.status_code, elapsed


def _socratic(headers):
    async def call(client):
        return await client.post(
            "/api/ai/socratic",
            json={
                "item_id": "d2-missing-item",
                "item_content": "¿Cuánto es 2 + 2?",
                "course_id": "algebra_basica",
                "student_message": "¿por dónde empiezo?",
                "api_key": "sk-d2-test-only",
            },
            headers=headers,
        )

    return call


def _app_with(repo):
    import api.dependencies as deps
    from api.main import app

    deps._repo_instance = repo
    return app


def test_spec002_d2_a_slow_repository_call_does_not_block_other_requests(repo, monkeypatch):
    """US4-AS1, FR-024, SC-004: KatIA's chat waits 2 s on the repository; GET / answers
    meanwhile."""
    import api.dependencies as deps
    from tests.integration.conftest import headers_for

    uid = make_student(repo)
    headers = headers_for(repo, uid)

    def slow_item(self, item_id):
        time.sleep(2.0)
        return None

    monkeypatch.setattr(type(repo), "get_item_by_id", slow_item)
    previous = deps._repo_instance
    try:
        status, elapsed = asyncio.run(_health_while(_socratic(headers), _app_with(repo)))
    finally:
        deps._repo_instance = previous
    assert status == 200
    assert elapsed < 1.0, f"GET / waited {elapsed:.2f} s behind the repository call"


def test_spec002_d2_waiting_for_the_pool_does_not_block_the_loop(postgres_repo, monkeypatch):
    """US4-AS2: with the pool exhausted, an asynchronous handler waits for a connection in a
    worker thread; GET / answers meanwhile."""
    import api.dependencies as deps
    from tests.integration.conftest import headers_for

    uid = make_student(postgres_repo)
    headers = headers_for(postgres_repo, uid)
    repo = _new_repo(monkeypatch, _PG_URL)
    held = [repo.get_connection() for _ in range(5)]

    def release_later():
        time.sleep(2.0)
        for conn in held:
            repo.put_connection(conn)

    # The access-token check reads the user too: let it through, then exhaust the pool.
    original_auth = deps.authenticate_access_token

    def auth(token, _repo):
        return original_auth(token, postgres_repo)

    monkeypatch.setattr(deps, "authenticate_access_token", auth)
    previous = deps._repo_instance
    threading.Thread(target=release_later, daemon=True).start()
    try:
        status, elapsed = asyncio.run(_health_while(_socratic(headers), _app_with(repo)))
    finally:
        deps._repo_instance = previous
        repo._pool.closeall()
    assert status == 200
    assert elapsed < 1.0, f"GET / waited {elapsed:.2f} s behind the pool"


# ── FR-024: guard ───────────────────────────────────────────────────────────


def test_spec002_d2_no_repository_call_in_async_code():
    """FR-024 (AGENTS R17): no `async def` under api/ calls the repository or
    authenticate_access_token directly; such calls go through asyncio.to_thread or
    run_in_executor. get_repository() is allowed: it returns the instance the lifespan built."""
    import ast
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[2] / "api"
    blocking = {"authenticate_access_token"}
    offenders = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.AsyncFunctionDef):
                continue
            for node in ast.walk(fn):
                if not isinstance(node, ast.Call):
                    continue
                f = node.func
                name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
                owner = (
                    f.value.id
                    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                    else ""
                )
                if owner in ("repo", "repository") or name in blocking:
                    offenders.append(
                        f"{path.relative_to(root.parent)}:{node.lineno} {owner}.{name}".strip(".")
                    )
    assert offenders == []
