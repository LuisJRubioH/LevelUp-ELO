"""Argon2 reserves 64 MiB per hash: the process never runs more than a fixed number at once, so a
burst of logins (a class signing in together) cannot exhaust the instance's memory."""

import threading
import time

from src.infrastructure.security import hashing_service
from src.infrastructure.security.hashing_service import HashingService


class _CountingContext:
    """Stands in for passlib: records how many hash operations run at the same time."""

    def __init__(self):
        self.running = 0
        self.peak = 0
        self._lock = threading.Lock()

    def _work(self, *_args):
        with self._lock:
            self.running += 1
            self.peak = max(self.peak, self.running)
        time.sleep(0.05)
        with self._lock:
            self.running -= 1

    def hash(self, password):
        self._work()
        return "hash"

    def verify(self, password, hashed):
        self._work()
        return True

    def verify_and_update(self, password, hashed):
        self._work()
        return True, None


def _burst(calls):
    threads = [threading.Thread(target=call) for call in calls]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def test_concurrent_password_hashing_is_bounded():
    service = HashingService()
    other = HashingService()
    counter = _CountingContext()
    service.pwd_context = counter
    other.pwd_context = counter

    calls = []
    for _ in range(4):
        calls += [
            lambda: service.verify_and_update("pw", "h"),
            lambda: other.verify_and_update("pw", "h"),
            lambda: service.hash_password("pw"),
            lambda: other.verify_password("pw", "h"),
        ]
    _burst(calls)

    assert counter.running == 0
    assert counter.peak == hashing_service.MAX_CONCURRENT_HASHES


def test_a_failing_hash_releases_its_slot():
    service = HashingService()

    class _Failing:
        def verify_and_update(self, password, hashed):
            raise ValueError("malformed hash")

    service.pwd_context = _Failing()
    for _ in range(hashing_service.MAX_CONCURRENT_HASHES + 1):
        try:
            service.verify_and_update("pw", "not-a-hash")
        except ValueError:
            pass

    counter = _CountingContext()
    service.pwd_context = counter
    _burst([lambda: service.hash_password("pw")])
    assert counter.peak == 1
