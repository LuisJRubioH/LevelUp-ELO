"""
Survey 007 V22 (`docs/sdd/pvp-survey.md` § 7), owner decision 2026-10-20: orphaned PvP matches
were closed only at bootstrap, which in a deployment runs once in `migrate.py` — a match cut off
by a restart stayed `active` until the next deploy. The API now sweeps them periodically
(`expire_stale_pvp_matches`: active for more than 600 s → abandoned, no rating change; a real
match lasts 180 s, so a live one is never touched). Shutting down only stops the sweep: it never
closes a match (the owner chose not to, so nobody loses a game in progress).
"""

import asyncio
import threading

from api.websocket import pvp


class _Repo:
    def __init__(self, fail_first=False):
        self.calls, self.threads, self.fail_first = 0, [], fail_first

    def expire_stale_pvp_matches(self, max_age_seconds=600):
        self.calls += 1
        self.threads.append(threading.current_thread())
        if self.fail_first and self.calls == 1:
            raise RuntimeError("database unavailable")
        return 0


def _run_sweep_for(repo, seconds):
    async def scenario():
        task = asyncio.create_task(pvp.sweep_orphaned_matches(repo, every_seconds=0.01))
        await asyncio.sleep(seconds)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(scenario())


def test_the_sweep_runs_periodically_off_the_event_loop():
    repo = _Repo()

    _run_sweep_for(repo, 0.1)

    assert repo.calls >= 2
    assert all(t is not threading.main_thread() for t in repo.threads)  # R17: asyncio.to_thread


def test_a_failed_pass_does_not_stop_the_sweep():
    repo = _Repo(fail_first=True)

    _run_sweep_for(repo, 0.1)

    assert repo.calls >= 2


def test_the_api_runs_the_sweep_and_stopping_it_closes_no_match(monkeypatch):
    seen = {"started": False, "cancelled": False}

    async def fake_sweep(repo, every_seconds=pvp.ORPHAN_SWEEP_EVERY_S):
        seen["started"] = True
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            seen["cancelled"] = True
            raise

    monkeypatch.setattr(pvp, "sweep_orphaned_matches", fake_sweep)
    # The lifespan alone, not a second TestClient: binding the notifications loop to this
    # short-lived loop would break the session's shared client (`api_client`).
    from api.websocket import notifications

    monkeypatch.setattr(notifications, "bind_event_loop", lambda loop: None)
    from api.main import app, lifespan

    async def run_the_app():
        async with lifespan(app):
            await asyncio.sleep(0)  # let the sweep task start

    asyncio.run(run_the_app())

    assert seen == {"started": True, "cancelled": True}
