"""
api/websocket/limits.py
=======================
Spec 007 FR-051: the limits of one League socket. Pure — no I/O; the clock is injected.

A frame over `max_frame_bytes` is dropped. Frames are also rate-limited by a token bucket that
holds `per_second` frames and refills at `per_second` per second; a frame with no token left is
dropped. `abuse_limit` dropped frames within `abuse_window` seconds make the socket abusive: the
endpoint then closes it with 4429.
"""

import time
from collections import deque
from typing import Callable


class SocketLimits:
    def __init__(
        self,
        max_frame_bytes: int,
        per_second: int,
        abuse_limit: int,
        abuse_window: float = 10.0,
        clock: Callable[[], float] = time.monotonic,
    ):
        self._max_frame_bytes = max_frame_bytes
        self._rate = float(per_second)
        self._tokens = float(per_second)
        self._abuse_limit = abuse_limit
        self._abuse_window = abuse_window
        self._clock = clock
        self._last = clock()
        self._drops: deque[float] = deque()

    def accept(self, frame_len: int) -> bool:
        """True when a frame of `frame_len` bytes may be read; False when it is dropped."""
        now = self._clock()
        self._tokens = min(self._rate, self._tokens + (now - self._last) * self._rate)
        self._last = now
        if frame_len > self._max_frame_bytes or self._tokens < 1.0:
            self._drops.append(now)
            return False
        self._tokens -= 1.0
        return True

    def abusive(self) -> bool:
        """True when `abuse_limit` frames were dropped within the last `abuse_window` seconds."""
        horizon = self._clock() - self._abuse_window
        while self._drops and self._drops[0] <= horizon:
            self._drops.popleft()
        return len(self._drops) >= self._abuse_limit
