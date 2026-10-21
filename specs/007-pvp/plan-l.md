# Plan — spec 007, delivery L: socket and process limits

**Spec**: [spec.md](spec.md) § Deliveries, L (US5; FR-050, FR-051, FR-052) · **Branch**: `007-l`,
from `redesign` · **Date**: 2026-10-20 · **Status**: approved (owner, 2026-10-20); implemented

## Summary

Today a student can hold any number of League sockets; a socket can send frames of any size
(uvicorn accepts up to 16 MB) and any number of messages; and the API refuses more than one worker
only when `WEB_CONCURRENCY` says so — `uvicorn --workers 2` or a second instance starts silently,
and players in different processes never meet (AGENTS.md R18). Delivery L adds one live League
socket per student, a 4 KB frame cap and a 5 messages/second rate per socket, and a start-up guard
that catches more than one worker by any route on the same host.

## Constitution Check (1.2.0)

| Principle | L |
|---|---|
| Security (VI) | limits are server-side; a refused or closed socket gets a code and a reason, never exception text |
| One source of truth (II) | the numbers are settings with the owner's defaults (4096 bytes, 5/s), read in one place |
| Layers (III) | the rate/size logic is a pure helper in `api/websocket/limits.py` (no I/O, fake clock in tests); no domain or repository change |
| Dual database (IV, R1) | no repository and no schema change; the integration tests still run on both engines through `live_api` |
| Async (R17) | the checks run on the event loop with no I/O; nothing new is called under `_lock` |
| Single process (R18) | FR-052 enforces it; the doc note in AGENTS R18 and `docs/arquitectura.md` names the new guard |
| Simplicity (VII) | no new dependency; one in-memory registry, one token bucket per socket, one file lock |

## Design

### FR-050 — one live League socket per student (US5-AS1)

- `api/websocket/connections.py` already registers every authenticated socket per user (spec 004
  FR-027). L adds a separate registry, `league_sockets: dict[int, WebSocket]`, in
  `api/websocket/pvp.py`: set after authentication and before the lobby, cleared in the endpoint's
  `finally`.
- A second League socket of the same student, in any subject and any phase, is closed with
  **4409** «Ya tienes la Liga abierta en otra pestaña.» before it touches the lobby; the first is
  unchanged.
- **Overlap with delivery G (FR-023, D6).** FR-023 says the same thing in terms of the queue and
  the match. L owns the mechanism (the per-student registry and code 4409); G cites L's test for
  FR-023 and only adds what is G's: the notice wording reviewed with the other refusals of FR-024.
  If G ships first, it builds this registry and L only adds the frame and rate limits.
- **Reconnect (delivery F, FR-041/US4-AS3).** A dropped connection can stay half-open until the
  WebSocket ping times out (uvicorn: 20 s + 20 s). Under L alone, a student who reconnects in that
  window is refused with 4409 and can retry. Delivery F's resume path replaces the stale socket;
  L does not try to solve it.

### FR-051 — frame size and message rate (US5-AS2)

- **In the receive loop**, for every frame of a League socket (including the first, the token):
  - over `PVP_MAX_FRAME_BYTES` (default **4096**, UTF-8 length) → dropped unparsed;
  - beyond `PVP_MAX_MESSAGES_PER_SECOND` (default **5**; a token bucket of 5 refilled at 5/s) →
    dropped unparsed.
  A dropped frame gets no reply, as a malformed one already does (V12).
- **Persisting abuse closes the socket:** `PVP_ABUSE_LIMIT` dropped frames (default **10**) within
  10 s → close **4429** «Demasiados mensajes. Vuelve a entrar a la Liga.». In a match this is the
  player leaving; the existing 180 s / abandonment rules apply (F changes them later).
- **Server backstop (decided: O-L1):** start uvicorn with `--ws-max-size 65536` in
  `render.yaml`. Without it uvicorn buffers frames up to 16 MB before the application can drop
  them. The backstop affects every WebSocket (notifications too), so it is set well above 4 KB;
  a frame over it is closed by uvicorn with 1009, before the app sees it.
- The helper `api/websocket/limits.py::SocketLimits(clock)` exposes `accept(frame_len) -> bool`
  and `abusive() -> bool`; pure and unit-tested.

### FR-052 — one worker in production by any route

- Today `settings.validate_runtime()` refuses `WEB_CONCURRENCY > 1` only. `uvicorn --workers N`
  and gunicorn workers spawn N processes that each run the lifespan, and none of them sees a
  variable.
- **Detection (decided: O-L2):** in the lifespan, in production, take an exclusive,
  non-blocking `fcntl.flock` on a fixed file (`PVP_SINGLE_PROCESS_LOCK`, default
  `/tmp/oulad-api.lock`), held for the life of the process. A second worker on the same host fails
  to take it and refuses to start with the R18 message. The lock dies with the process, so a
  restart never sees a stale lock.
- **Limit:** a file lock cannot see a second Render instance on another machine. That stays
  covered by `render.yaml` (one instance) and the doc note. The alternative that also covers it — a
  PostgreSQL session advisory lock held by a dedicated connection — costs one permanent
  connection of the Supabase free tier's five (R4), so it is not recommended now.
- `WEB_CONCURRENCY > 1` keeps its current refusal; the lock is in addition.
- **Doc:** AGENTS.md R18 and `docs/arquitectura.md` § Límites conocidos name the lock.

### Frontend

- `frontend/src/hooks/usePvpMatch.ts`: `CLOSE_NOTICES` gains 4409 and 4429. The existing Spanish
  literals (4001, 4404, 4500 and the fallbacks) move to i18n with them, under
  `league.closeNotices.*` in `es` and `en`; #120 left them out of scope.
- No other screen change.

### Settings

`api/config.py`: `pvp_max_frame_bytes=4096`, `pvp_max_messages_per_second=5`,
`pvp_abuse_limit=10`, `pvp_single_process_lock="/tmp/oulad-api.lock"`. The first three are O2's
starting values (owner, 2026-10-20), tunable without a code change.

## Tests (written first; each fails on today's code)

| Test | Proves | Where |
|---|---|---|
| `test_spec007_a_second_league_socket_is_refused` | FR-050, US5-AS1: second socket closed 4409; the first still gets `game_start` and plays | `tests/integration/test_pvp_limits.py` (uvicorn, both engines) |
| `test_spec007_an_oversized_frame_is_dropped` | FR-051, US5-AS2: a 5 KB frame gets no reply; the next answer is judged | same file |
| `test_spec007_a_burst_beyond_the_rate_is_dropped` | FR-051, US5-AS2: of 6 answers in under a second, the 6th gets no `answer_result`; after a second answers are judged again | same file |
| `test_spec007_persisting_abuse_closes_the_socket` | FR-051, US5-AS2: 10 dropped frames → close 4429 | same file |
| `test_spec007_socket_limits_*` | the token bucket and the abuse window with a fake clock | `tests/unit/api/test_pvp_limits.py` |
| `test_spec007_a_second_worker_refuses_to_start` | FR-052: two processes start the lifespan in production with the same lock path; the second raises the R18 error | `tests/api/test_single_worker.py` (subprocesses) |
| `test_spec007_web_concurrency_is_still_refused` | FR-052: the existing guard is kept | same file |
| e2e `league.spec.ts`: «una segunda pestaña dice por qué» | the 4409 notice shown in the lobby | `frontend/e2e/league.spec.ts` |

All the existing PvP tests stay green; `test_pvp_waiting_player.py` and
`test_pvp_enrolment.py` exercise normal play under the new limits.

**Traceability rows to fill:** FR-050, FR-051, FR-052, US5-AS1, US5-AS2 (delivery L → closed).

## Risks

- **Legitimate bursts.** The client sends one answer per click, so 5/s leaves room; a stuck
  client retrying could hit 4429. The numbers are settings.
- **Half-open reconnects** refused for up to ~40 s (above); delivery F resolves it.
- **The lock file** must live on a writable local path. Render's `/tmp` is; a read-only
  filesystem would refuse to start, with a clear message rather than silently.
- **A second machine** is not detected (above, decision O-L2).

## Decisions (owner, 2026-10-20)

- **O-L1 — yes:** `render.yaml` starts uvicorn with `--ws-max-size 65536` as the server cap.
- **O-L2 — host file lock:** extra workers are detected with an exclusive host file lock, not a
  PostgreSQL advisory lock; a second machine stays out of reach and is documented.
- **O-L3 — yes:** close codes **4409** (second tab) and **4429** (abuse); delivery G's FR-024
  table lists them with the other refusals.
