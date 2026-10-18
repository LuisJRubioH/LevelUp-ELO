"""
Spec 004, delivery E6 (US10, FR-090 … FR-095): when the shared rate-limit store fails while the API
runs, the limits keep applying from memory, no request waits on the store once the failure is
known, recovery is probed in the background at most once per interval and carries over what memory
counted, entering and leaving are logged once each, and `/api/health` reports the state.

The shared store is played by `FlakyStore` (limits' memory storage that can be switched off), the
clock is fake and the probe runs inline, so every transition is deterministic. The client timeouts
are checked against a real Redis client talking to a socket that never answers.

[CHANGE] tests: they fail on the base branch, where a store failure answers 500.
"""

import logging
import socket
import time
import uuid
from types import SimpleNamespace

import pytest
from limits import parse
from limits.storage import MemoryStorage, storage_from_string
from limits.strategies import FixedWindowRateLimiter

from api import rate_limit
from api.config import settings
from api.dependencies import get_repository
from api.rate_limit import FailoverStorage, LimitsUnavailable

_SECRET_URI = "redis://default:s3cr3t-pass@10.0.0.5:6379/0"


class FlakyStore(MemoryStorage):
    """The shared store: limits' memory storage that fails like an unreachable Redis on demand."""

    def __init__(self):
        super().__init__()
        self.down = False
        self.calls = 0

    def _touch(self):
        self.calls += 1
        if self.down:
            raise ConnectionError(f"Error connecting to {_SECRET_URI}")

    def incr(self, key, expiry, amount=1):
        self._touch()
        return super().incr(key, expiry, amount=amount)

    def get(self, key):
        self._touch()
        return super().get(key)

    def get_expiry(self, key):
        self._touch()
        return super().get_expiry(key)

    def clear(self, key):
        self._touch()
        return super().clear(key)

    def check(self):
        self.calls += 1
        return not self.down


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def _failover(shared=None, **options):
    clock = FakeClock()
    shared = shared or FlakyStore()
    defaults = {"probe_interval": 10.0, "max_keys": 1000, "clock": clock, "spawn": lambda f: f()}
    storage = FailoverStorage(shared, **{**defaults, **options})
    return SimpleNamespace(
        shared=shared, clock=clock, storage=storage, limiter=FixedWindowRateLimiter(storage)
    )


@pytest.fixture
def api_failover():
    """The API's limiter with a FlakyStore behind the failover; restored afterwards."""
    target = rate_limit.limiter
    original = (target._storage, target._limiter)
    clock = FakeClock()
    shared = FlakyStore()
    rate_limit.use_failover_storage(
        target, shared, probe_interval=10.0, max_keys=1000, clock=clock, spawn=lambda f: f()
    )
    yield SimpleNamespace(shared=shared, clock=clock, storage=target._storage)
    target._storage, target._limiter = original
    target.reset()


_HASH = {}


def _student():
    repo = get_repository()
    if "hash" not in _HASH:
        _HASH["hash"] = repo.hashing.hash_password("password123")
    name = "e6_" + uuid.uuid4().hex[:12]
    conn = repo.get_connection()
    conn.execute(
        "INSERT INTO users (username, password_hash, role, approved, active, education_level)"
        " VALUES (?, ?, 'student', 1, 1, 'colegio')",
        (name, _HASH["hash"]),
    )
    conn.commit()
    conn.close()
    return name


def _login(client, username, password="password123"):
    return client.post("/api/auth/login", json={"username": username, "password": password})


# ── FR-090, US10-AS1: the limits keep applying from memory ───────────────────


def test_spec004_limits_keep_applying_from_memory_when_the_store_fails():
    """FR-090: same configured limit, counted in memory once the store fails."""
    f = _failover()
    three = parse("3/minute")
    assert f.limiter.hit(three, "k")
    f.shared.down = True

    hits = [f.limiter.hit(three, "k") for _ in range(4)]

    assert hits == [True, True, True, False]
    assert f.storage.degraded


def test_spec004_api_limits_and_health_during_an_outage(api_client, api_failover):
    """US10-AS1: with the store failing, login keeps its per-account limit and `/api/health`
    answers 200 with a degraded state, without the store's address or password."""
    api_failover.shared.down = True
    name = _student()

    statuses = [_login(api_client, name).status_code for _ in range(11)]
    health = api_client.get("/api/health")

    assert statuses == [200] * 10 + [429]
    assert health.status_code == 200
    assert health.json()["limits"] == "degraded"
    assert health.json()["status"] == "degraded"
    assert "s3cr3t" not in health.text and "10.0.0.5" not in health.text


# ── FR-091: timeouts, no waiting once the failure is known, controlled probing ─


def test_spec004_no_request_calls_the_store_once_its_failure_is_known():
    """FR-091: after the first failure, requests are served from memory without touching the store
    until the probe interval has passed; then one probe, not one per request."""
    f = _failover()
    f.shared.down = True
    f.limiter.hit(parse("100/minute"), "k")
    calls_after_failure = f.shared.calls

    for _ in range(20):
        f.limiter.hit(parse("100/minute"), "k")
    assert f.shared.calls == calls_after_failure

    f.clock.now += 10.0
    for _ in range(20):
        f.limiter.hit(parse("100/minute"), "k")
    assert f.shared.calls == calls_after_failure + 1  # one probe (check), still down


def test_spec004_store_calls_are_bounded_by_their_timeouts(monkeypatch):
    """FR-091: a real Redis client with the configured timeouts and no client retries. Against a
    socket that never answers, the first call ends after about one timeout and goes to memory;
    the next ones do not wait at all."""
    silent = socket.socket()
    silent.bind(("127.0.0.1", 0))
    silent.listen(8)
    monkeypatch.setattr(settings, "rate_limit_storage_uri", "redis://127.0.0.1:1/0")
    monkeypatch.setattr(settings, "rate_limit_storage_connect_timeout", 0.3)
    monkeypatch.setattr(settings, "rate_limit_storage_timeout", 0.3)
    options = rate_limit._shared_store_options()
    assert options["socket_connect_timeout"] == 0.3 and options["socket_timeout"] == 0.3
    shared = storage_from_string(f"redis://127.0.0.1:{silent.getsockname()[1]}/0", **options)
    f = _failover(shared, spawn=lambda f: None)
    try:
        started = time.monotonic()
        assert f.limiter.hit(parse("5/minute"), "k")
        first = time.monotonic() - started

        started = time.monotonic()
        for _ in range(4):
            f.limiter.hit(parse("5/minute"), "k")
        rest = time.monotonic() - started
    finally:
        silent.close()

    assert 0.25 <= first < 1.5
    assert rest < 0.1
    assert not f.limiter.hit(parse("5/minute"), "k")  # the sixth, counted in memory


# ── FR-092, US10-AS2: back to the store without a new allowance ──────────────


def test_spec004_recovery_carries_memory_counts_over_to_the_store():
    """FR-092, US10-AS2: what memory counted is added to the store on recovery, so a key keeps
    what it spent before and during the outage; memory is emptied."""
    f = _failover()
    five = parse("5/minute")
    assert f.limiter.hit(five, "before") and f.limiter.hit(five, "before")  # 2 in the store
    f.shared.down = True
    for _ in range(2):
        f.limiter.hit(five, "before")  # 2 in memory
    for _ in range(3):
        f.limiter.hit(five, "during")  # a key counted only during the outage

    f.shared.down = False
    f.clock.now += 10.0
    f.limiter.hit(five, "other")  # triggers the probe; counted in memory, then carried over

    assert not f.storage.degraded
    assert f.shared.get(five.key_for("before")) == 4
    assert f.shared.get(five.key_for("during")) == 3
    assert f.shared.get(five.key_for("other")) == 1
    assert f.limiter.hit(five, "before")  # the 5th
    assert not f.limiter.hit(five, "before")  # the 6th: no new allowance
    assert [f.limiter.hit(five, "during") for _ in range(3)] == [True, True, False]


def test_spec004_a_failed_probe_keeps_the_fallback():
    """FR-091/FR-092: a probe that fails leaves the counters in memory and waits another
    interval; the store is used again only after a successful probe."""
    f = _failover()
    five = parse("5/minute")
    f.shared.down = True
    f.limiter.hit(five, "k")
    f.clock.now += 10.0
    f.limiter.hit(five, "k")  # probe fails

    assert f.storage.degraded
    f.shared.down = False
    f.clock.now += 5.0
    f.limiter.hit(five, "k")  # before the next interval: no probe
    assert f.storage.degraded

    f.clock.now += 5.0
    f.limiter.hit(five, "k")
    assert not f.storage.degraded
    assert f.shared.get(five.key_for("k")) == 4


# ── FR-093, US10-AS5: one log entry in, one out ──────────────────────────────


def test_spec004_entering_and_leaving_are_logged_once_each(caplog):
    """FR-093, US10-AS5: an outage of many requests logs one entry for entering and one for
    leaving, neither with the store's address or password."""
    f = _failover()
    with caplog.at_level(logging.DEBUG, logger="api.rate_limit"):
        f.shared.down = True
        for _ in range(50):
            f.limiter.hit(parse("100/minute"), "k")
            f.clock.now += 1.0  # several failed probes along the way
        f.shared.down = False
        f.clock.now += 10.0
        for _ in range(50):
            f.limiter.hit(parse("100/minute"), "k")

    warnings = [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]
    assert len([m for m in warnings if "unreachable" in m]) == 1
    assert len([m for m in warnings if "recovered" in m]) == 1
    assert len(warnings) == 2
    assert "s3cr3t" not in caplog.text and "10.0.0.5" not in caplog.text


# ── FR-094: health reports normal, degraded or unavailable ───────────────────


def test_spec004_health_reports_the_limits_state(api_client, api_failover):
    """FR-094: 200 "normal" with the store answering; 200 "degraded" while memory counts; back to
    "normal" after recovery."""
    normal = api_client.get("/api/health")
    api_failover.shared.down = True
    degraded = api_client.get("/api/health")
    api_failover.shared.down = False
    api_failover.clock.now += 10.0
    recovered = api_client.get("/api/health")

    assert (normal.status_code, normal.json()["limits"], normal.json()["status"]) == (
        200,
        "normal",
        "ok",
    )
    assert (degraded.status_code, degraded.json()["limits"]) == (200, "degraded")
    assert (recovered.status_code, recovered.json()["limits"]) == (200, "normal")


# ── FR-095, US10-AS3: both mechanisms failing ────────────────────────────────


@pytest.mark.parametrize("cause", ["fallback_disabled", "fallback_full"])
def test_spec004_without_store_or_fallback_limited_requests_are_refused(
    api_client, api_failover, cause
):
    """FR-095, US10-AS3: with the store down and memory unable to count — disabled because more
    than one process serves, or full — a limited request is refused and `/api/health` answers
    503, without the store's address."""
    storage = api_failover.storage
    if cause == "fallback_disabled":
        storage._fallback_enabled = False
    else:
        storage._memory._max_keys = 0
    api_failover.shared.down = True

    login = _login(api_client, _student())
    health = api_client.get("/api/health")

    assert login.status_code == 503
    assert login.headers.get("retry-after") == "60"
    assert health.status_code == 503
    assert "s3cr3t" not in login.text + health.text


def test_spec004_memory_fallback_needs_a_single_process(monkeypatch):
    """FR-090: memory counts the limits only while one process serves (WEB_CONCURRENCY=1)."""
    target = SimpleNamespace(_storage=FlakyStore(), _limiter=None)
    monkeypatch.setattr(settings, "web_concurrency", 2)
    rate_limit.use_failover_storage(target, clock=FakeClock(), spawn=lambda f: f())
    target._storage._shared.down = True

    with pytest.raises(LimitsUnavailable):
        target._limiter.hit(parse("5/minute"), "k")
    assert target._storage.state() == "unavailable"


def test_spec004_the_api_limiter_uses_the_failover_with_a_shared_store(monkeypatch):
    """FR-090/FR-091: with a shared store configured, the limiter that routes and login use sits
    behind the failover, with the configured timeouts (guards slowapi's private attributes)."""
    from slowapi import Limiter

    monkeypatch.setattr(settings, "rate_limit_storage_uri", "redis://127.0.0.1:1/0")
    target = Limiter(
        key_func=lambda r: "k",
        storage_uri=settings.rate_limit_storage_uri,
        storage_options=rate_limit._shared_store_options(),
    )
    rate_limit.use_failover_storage(target)

    assert isinstance(target.limiter.storage, FailoverStorage)
    assert target.limiter.storage is target._storage
    shared_pool = target._storage._shared.storage.connection_pool.connection_kwargs
    assert shared_pool["socket_timeout"] == settings.rate_limit_storage_timeout
    assert shared_pool["socket_connect_timeout"] == settings.rate_limit_storage_connect_timeout
    assert target.limiter.hit(parse("1/minute"), "k")  # refused connection → memory
    assert not target.limiter.hit(parse("1/minute"), "k")
