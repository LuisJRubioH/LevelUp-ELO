"""
Spec 007 FR-051 (delivery L): the per-socket limits of the League, with a fake clock.

`api/websocket/limits.py::SocketLimits` is pure: a token bucket of `per_second` frames refilled at
`per_second` per second, a frame-size cap, and an abuse window — `abuse_limit` dropped frames
within `abuse_window` seconds mark the socket as abusive.
"""

from api.websocket.limits import SocketLimits


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def _limits(clock, **overrides):
    options = {"max_frame_bytes": 4096, "per_second": 5, "abuse_limit": 10, "clock": clock}
    options.update(overrides)
    return SocketLimits(**options)


def test_spec007_socket_limits_accept_up_to_the_rate_then_drop():
    clock = FakeClock()
    limits = _limits(clock)

    accepted = [limits.accept(10) for _ in range(6)]

    assert accepted == [True, True, True, True, True, False]


def test_spec007_socket_limits_refill_after_a_second():
    clock = FakeClock()
    limits = _limits(clock)
    for _ in range(5):
        limits.accept(10)
    assert not limits.accept(10)

    clock.now += 1.0

    assert [limits.accept(10) for _ in range(6)] == [True] * 5 + [False]


def test_spec007_socket_limits_refill_never_exceeds_the_burst():
    clock = FakeClock()
    limits = _limits(clock)

    clock.now += 60.0

    assert [limits.accept(10) for _ in range(6)] == [True] * 5 + [False]


def test_spec007_socket_limits_drop_an_oversized_frame_without_spending_the_rate():
    clock = FakeClock()
    limits = _limits(clock)

    assert not limits.accept(4097)
    assert limits.accept(4096)
    assert [limits.accept(10) for _ in range(4)] == [True] * 4


def test_spec007_socket_limits_abuse_is_ten_drops_within_ten_seconds():
    clock = FakeClock()
    limits = _limits(clock)

    for _ in range(9):
        limits.accept(5000)
    assert not limits.abusive()
    limits.accept(5000)

    assert limits.abusive()


def test_spec007_socket_limits_old_drops_leave_the_abuse_window():
    clock = FakeClock()
    limits = _limits(clock)
    for _ in range(9):
        limits.accept(5000)

    clock.now += 10.5
    limits.accept(5000)

    assert not limits.abusive()


def test_spec007_socket_limits_accepted_frames_are_never_abuse():
    clock = FakeClock()
    limits = _limits(clock)

    for _ in range(100):
        clock.now += 0.25
        assert limits.accept(100)

    assert not limits.abusive()
