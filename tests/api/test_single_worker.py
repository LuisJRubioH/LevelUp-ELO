"""
Spec 007 FR-052 (delivery L): one worker in production, whatever starts it.

`WEB_CONCURRENCY > 1` was the only route the API refused; `uvicorn --workers N` and gunicorn
workers start N processes that each run the lifespan and see no variable. In production the
lifespan now takes an exclusive, non-blocking lock on a host file for the life of the process: a
second process on the same host cannot take it and refuses to start with the R18 message.
"""

import asyncio
import subprocess
import sys
import textwrap

import pytest

import api.main as main_module
from api.config import settings

_HOLD = textwrap.dedent(
    """
    import sys, time
    from api.single_process import hold_single_process_lock
    handle = hold_single_process_lock(sys.argv[1])
    print("held", flush=True)
    time.sleep(60)
    """
)


@pytest.fixture
def production(monkeypatch, tmp_path):
    """Production settings that pass `validate_runtime`, with this test's lock path."""
    lock = tmp_path / "api.lock"
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "database_url", "postgresql://unused")
    monkeypatch.setattr(settings, "jwt_secret_key", "x" * 40)
    monkeypatch.setattr(settings, "cors_origins", ["https://example.org"])
    monkeypatch.setattr(settings, "rate_limit_storage_uri", "redis://unused:6379")
    monkeypatch.setattr(settings, "web_concurrency", 1)
    monkeypatch.setattr(settings, "pvp_single_process_lock", str(lock))
    # The repository is not what is tested here: no database is opened.
    import api.dependencies as deps

    monkeypatch.setattr(deps, "get_repository", lambda: object())
    import api.websocket.notifications as notifications

    monkeypatch.setattr(notifications, "bind_event_loop", lambda loop: None)
    return lock


# The lock is POSIX (`fcntl`), as the production host is; Windows has no `fcntl`.
posix_only = pytest.mark.skipif(sys.platform == "win32", reason="fcntl: POSIX only")


async def _start_and_stop():
    async with main_module.lifespan(main_module.app):
        pass


@posix_only
def test_spec007_a_second_worker_refuses_to_start(production):
    """FR-052: another process holds the lock (a first worker); this one refuses to start with
    the R18 message."""
    holder = subprocess.Popen(
        [sys.executable, "-c", _HOLD, str(production)],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout.readline().strip() == "held"

        with pytest.raises(RuntimeError, match="R18"):
            asyncio.run(_start_and_stop())
    finally:
        holder.kill()
        holder.wait()


@posix_only
def test_spec007_a_single_worker_starts_and_a_restart_is_not_blocked(production):
    """FR-052: alone, the worker starts; the lock dies with its holder, so a restart after it
    exited starts too."""
    asyncio.run(_start_and_stop())

    holder = subprocess.Popen(
        [sys.executable, "-c", _HOLD, str(production)], stdout=subprocess.PIPE
    )
    holder.stdout.readline()
    holder.kill()
    holder.wait()

    asyncio.run(_start_and_stop())


def test_spec007_web_concurrency_is_still_refused(production, monkeypatch):
    """FR-052: the existing guard is kept."""
    monkeypatch.setattr(settings, "web_concurrency", 2)

    with pytest.raises(RuntimeError, match="WEB_CONCURRENCY"):
        asyncio.run(_start_and_stop())
