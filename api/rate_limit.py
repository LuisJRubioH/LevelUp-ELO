"""Rate limiting compartido para operaciones costosas de la API."""

import hashlib
import logging
import math
import threading
import time

import jwt
from jwt.exceptions import InvalidTokenError
from limits import parse
from limits.storage import Storage
from limits.strategies import FixedWindowRateLimiter
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.config import settings

logger = logging.getLogger(__name__)


def client_ip(request) -> str:
    """Login y registro: quien llama aún no tiene cuenta, así que solo cuenta su origen."""
    return f"ip:{get_remote_address(request)}"


def _client_key(request) -> str:
    """Separa usuarios autenticados por cuenta, sin almacenar ni registrar su token.

    Por cuenta y no por token: un token nuevo (refresh o login) no reinicia el límite, y los
    estudiantes detrás de la misma IP del colegio no lo comparten. Una cabecera que no es un
    access token válido cuenta como ausente; si no, una inventada por petición sería un cupo nuevo.
    """
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        try:
            payload = jwt.decode(
                authorization[7:], settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
        except InvalidTokenError:
            payload = {}
        if payload.get("type") == "access" and payload.get("sub"):
            return f"user:{payload['sub']}"
    return client_ip(request)


class LimitsUnavailable(Exception):
    """Spec 004 FR-095: neither the shared store nor its memory fallback can count a limit."""


class _MemoryCounters:
    """Fixed-window counters in this process's memory: key → [count, expiry on `clock`].

    Not thread-safe by itself: `FailoverStorage` calls it under its lock.
    """

    def __init__(self, clock, max_keys: int):
        self._clock = clock
        self._max_keys = max_keys
        self._counters: dict[str, list[float]] = {}

    def _live(self, key: str):
        entry = self._counters.get(key)
        if entry is not None and entry[1] <= self._clock():
            del self._counters[key]
            return None
        return entry

    def _purge(self) -> None:
        now = self._clock()
        for key in [k for k, (_, expires) in self._counters.items() if expires <= now]:
            del self._counters[key]

    def has_room(self) -> bool:
        if len(self._counters) >= self._max_keys:
            self._purge()
        return len(self._counters) < self._max_keys

    def incr(self, key: str, expiry: int, amount: int) -> int:
        entry = self._live(key)
        if entry is None:
            if not self.has_room():
                raise LimitsUnavailable("memory fallback is full")
            entry = self._counters[key] = [0, self._clock() + expiry]
        entry[0] += amount
        return int(entry[0])

    def get(self, key: str) -> int:
        entry = self._live(key)
        return int(entry[0]) if entry else 0

    def remaining(self, key: str) -> float:
        entry = self._live(key)
        return entry[1] - self._clock() if entry else 0.0

    def live_items(self):
        """[(key, count, seconds left)] of the counters still inside their window."""
        self._purge()
        now = self._clock()
        return [(k, int(count), expires - now) for k, (count, expires) in self._counters.items()]

    def pop(self, key: str) -> None:
        self._counters.pop(key, None)

    def clear(self) -> None:
        self._counters.clear()


class FailoverStorage(Storage):
    """Spec 004 E6 (FR-090 … FR-095; constitution 1.1.0, rate-limit store fallback).

    Counts in the shared store while it answers. The first failure switches every counter to this
    process's memory, with the same limits, and is logged once; from then on no request calls the
    store. A background probe checks it at most once per `probe_interval`, and on success adds what
    memory counted to the store before using it again, so no key gets a new allowance; that is
    logged once too. If memory cannot count either (fallback disabled, or full), the limited request
    is refused with `LimitsUnavailable`. A restart loses the memory counters.
    """

    STORAGE_SCHEME = None

    def __init__(
        self,
        shared: Storage,
        *,
        probe_interval: float,
        max_keys: int,
        fallback_enabled: bool = True,
        clock=time.monotonic,
        spawn=None,
    ):
        super().__init__()
        self._shared = shared
        self._probe_interval = probe_interval
        self._fallback_enabled = fallback_enabled
        self._clock = clock
        self._spawn = spawn or self._spawn_thread
        self._memory = _MemoryCounters(clock, max_keys)
        self._lock = threading.Lock()
        self._degraded = False
        self._probing = False
        self._next_probe = 0.0

    @property
    def base_exceptions(self):
        return LimitsUnavailable

    @staticmethod
    def _spawn_thread(target) -> None:
        threading.Thread(target=target, name="rate-limit-store-probe", daemon=True).start()

    # ── State ────────────────────────────────────────────────────────────────

    @property
    def degraded(self) -> bool:
        return self._degraded

    def _enter_degraded(self, exc: BaseException) -> None:
        with self._lock:
            if self._degraded:
                return
            self._degraded = True
            self._next_probe = self._clock() + self._probe_interval
        # The class only: a store error may carry its address.
        logger.warning(
            "Rate-limit store unreachable (%s): limits are counted in memory until it recovers.",
            type(exc).__name__,
        )

    def _probe_due(self) -> bool:
        """Under the lock: whether this caller should start the recovery probe."""
        if self._degraded and not self._probing and self._clock() >= self._next_probe:
            self._probing = True
            return True
        return False

    def _probe(self) -> None:
        carried = None
        try:
            if self._shared.check():
                with self._lock:
                    carried = 0
                    for key, count, seconds_left in self._memory.live_items():
                        self._shared.incr(key, max(1, math.ceil(seconds_left)), amount=count)
                        self._memory.pop(key)
                        carried += 1
                    self._memory.clear()
                    self._degraded = False
        except Exception as exc:
            # Still degraded; counters not yet carried over stay in memory for the next probe.
            logger.debug("Rate-limit store probe failed: %s", type(exc).__name__)
            carried = None
        finally:
            with self._lock:
                self._probing = False
                self._next_probe = self._clock() + self._probe_interval
        if carried is not None:
            logger.warning(
                "Rate-limit store recovered: limits use it again (%d counters carried over).",
                carried,
            )

    def _in_memory(self, operation):
        """Run `operation(memory)` under the lock while degraded; None if the store is back."""
        with self._lock:
            if not self._degraded:
                return None
            if not self._fallback_enabled:
                raise LimitsUnavailable("memory fallback disabled")
            result = (operation(self._memory),)
            start_probe = self._probe_due()
        if start_probe:
            self._spawn(self._probe)
        return result

    def _call(self, shared_operation, memory_operation):
        if not self._degraded:
            try:
                return shared_operation()
            except Exception as exc:
                self._enter_degraded(exc)
        result = self._in_memory(memory_operation)
        if result is None:  # recovered meanwhile
            return self._call(shared_operation, memory_operation)
        return result[0]

    def state(self) -> str:
        """`/api/health` (FR-094): "normal", "degraded" or "unavailable"."""
        if not self._degraded:
            if self._shared.check():
                return "normal"
            self._enter_degraded(ConnectionError("health check"))
        with self._lock:
            start_probe = self._probe_due()
        if start_probe:
            self._spawn(self._probe)
        with self._lock:
            if not self._degraded:
                return "normal"
            usable = self._fallback_enabled and self._memory.has_room()
        return "degraded" if usable else "unavailable"

    # ── limits.storage.Storage ───────────────────────────────────────────────

    def incr(self, key: str, expiry: int, amount: int = 1) -> int:
        return self._call(
            lambda: self._shared.incr(key, expiry, amount=amount),
            lambda memory: memory.incr(key, expiry, amount),
        )

    def get(self, key: str) -> int:
        return self._call(lambda: self._shared.get(key), lambda memory: memory.get(key))

    def get_expiry(self, key: str) -> float:
        return self._call(
            lambda: self._shared.get_expiry(key),
            lambda memory: time.time() + memory.remaining(key),
        )

    def check(self) -> bool:
        return self.state() != "unavailable"

    def reset(self):
        with self._lock:
            self._memory.clear()
        return None if self._degraded else self._shared.reset()

    def clear(self, key: str) -> None:
        with self._lock:
            self._memory.pop(key)
        if not self._degraded:
            self._shared.clear(key)


def _is_memory_uri(uri: str) -> bool:
    return uri.strip().lower().startswith("memory://")


def _shared_store_options() -> dict:
    """Timeouts for the shared store's client (FR-091); one attempt per call, no client retries:
    a failure goes to the memory fallback instead of being retried while a request waits.
    For the Redis and Valkey URIs the deployment uses; other schemes keep their client defaults."""
    scheme = settings.rate_limit_storage_uri.strip().lower().split("://", 1)[0]
    if scheme in ("redis", "rediss", "redis+unix"):
        from redis.backoff import NoBackoff
        from redis.retry import Retry
    elif scheme in ("valkey", "valkeys", "valkey+unix"):
        from valkey.backoff import NoBackoff
        from valkey.retry import Retry
    else:
        return {}
    return {
        "socket_connect_timeout": settings.rate_limit_storage_connect_timeout,
        "socket_timeout": settings.rate_limit_storage_timeout,
        "retry": Retry(NoBackoff(), 0),
    }


limiter = Limiter(
    key_func=_client_key,
    storage_uri=settings.rate_limit_storage_uri,
    storage_options=_shared_store_options(),
)


def use_failover_storage(target: Limiter, shared: Storage | None = None, **options) -> None:
    """Put a `FailoverStorage` in front of `target`'s store. slowapi takes only a storage URI, so
    its storage and strategy are replaced after construction (checked by the E6 tests)."""
    defaults = {
        "probe_interval": settings.rate_limit_storage_probe_interval,
        "max_keys": settings.rate_limit_fallback_max_keys,
        # FR-090: memory counts the limits only while a single process serves (R18).
        "fallback_enabled": settings.web_concurrency <= 1,
    }
    storage = FailoverStorage(shared or target._storage, **{**defaults, **options})
    target._storage = storage
    target._limiter = FixedWindowRateLimiter(storage)


if not _is_memory_uri(settings.rate_limit_storage_uri):
    use_failover_storage(limiter)


def limits_state() -> str:
    """Spec 004 FR-094: the limits' state for `/api/health` — "normal", "degraded" or
    "unavailable". A process without a shared store (development, tests) counts in memory as
    configured: that is its normal state."""
    storage = limiter._storage
    if isinstance(storage, FailoverStorage):
        return storage.state()
    return "normal" if storage.check() else "unavailable"


def login_limit_key(account_id: int | None, identifier: str) -> str:
    """Spec 004 FR-006, FR-011: the counter a sign-in attempt goes to.

    An attempt that names an active account — by username or by email — counts for that account.
    Any other identifier counts for itself, after trimming outer spaces and ignoring letter case,
    and only as a one-way digest: the limit store holds no readable identifier (FR-011).
    """
    if account_id is not None:
        return f"account:{account_id}"
    digest = hashlib.sha256(identifier.strip().casefold().encode("utf-8")).hexdigest()
    return f"identifier:{digest}"


def login_allowed(key: str) -> bool:
    """Spec 004 FR-006, FR-007: count one attempt on the global and on the key's counter; False if
    either is over its limit for the current minute. Values come from settings at each call."""
    strategy = limiter.limiter
    overall = strategy.hit(parse(settings.rate_limit_login_global), "login", "all")
    account = strategy.hit(parse(settings.rate_limit_login_account), "login", key)
    return overall and account
