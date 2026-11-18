# QA follow-up: cold provider setup blocks the API

Date: 2026-11-17. Branch: `codex/qa-procedure-latency-review`, based on `main` at `c812bb0`
(PR #189 merged). Initial selector correction: `1936f9e`; complete correction: `e3f49c9`.

## Cause and scope

The procedure-review latency left open in the enrollment-isolation review is a real event-loop
stall. Before the already-threaded provider call, the async procedure handler calls `ai_target`
synchronously (`api/routers/student.py:740`). KatIA also imports the AI client before selection
inside its async handler (`api/routers/ai.py:64`), then calls the selector at line 107.

`api/ai_target.py:41` imports `ai_client`, whose line 2 imports `requests`. On a cold process,
that import initializes the SSL certificate bundle. Local profiling measured 0.643 s in
`SSLContext.load_verify_locations`, out of 0.763 s in `ai_target`. During this work, another
request could not enter the same ASGI event loop. Reusing the import cache hides this cost.

This violates AGENTS R17's rule for blocking I/O in async handlers and the responsiveness
covered by spec 005 FR-023. The shared process means other requests wait too (R18). No lost
answers, rating errors or League forfeits were established by this investigation.

## Measurements and control

Temporary local pytest instrumentation recorded only timestamps, thread names and function
names; no request bodies, keys or headers. It wrapped the real routes and retained the original
test's 1.0 s limit and the mock provider's 3 s wait.

| Observation | Selector execution | Selector duration | Health request duration |
|---|---|---|---|
| Baseline, cold process | ASGI event-loop thread | 969 ms | 841 ms |
| Baseline, module preloaded outside HTTP | ASGI event-loop thread, cached import | under 1 ms | 110 ms |
| Corrected, cold process | executor worker | 876 ms | 102 ms |

These timeline samples exercise procedure review. The particular instrumented baseline run
passed the 1.0 s assertion, but still blocked other
ASGI work until selector completion. Previous uninstrumented complete-suite runs measured
1.69–1.80 s and failed that assertion. The delay varies with the host and import cache.

With the correction, health completed at 0.405 s from the start of the trace, while provider
setup was still running until 0.976 s. The provider then spent its full three seconds waiting.
Thus the improvement did not depend on preloading the module or shortening the provider wait.

## Correction and regression

Both async handlers now await `asyncio.to_thread(ai_target, ...)`. Selection and its lazy
imports leave the event loop, following the pattern already used for database reads and the
provider calls. KatIA looks up `get_socratic_guidance` only after that worker has loaded the
module; the subsequent import is cached. The teacher analysis handler is synchronous and
already runs in a worker.
No public API, provider selection rule, timeout or key precedence changed.

The new parametrized regression explicitly holds the AI-client import until the test releases it,
even when the module is already cached and the provider functions have been stubbed.
While setup is blocked, the health request must finish and the review must remain unfinished.
This tests responsiveness without depending on the speed of a real certificate import.

- Before the correction: **2 failed**, 2 warnings, 5.05 s, exit 1. Both procedure and KatIA
  failed with `health request stalled behind provider setup`; cleanup released the held worker.
- The initial selector-only correction yielded **45 passed**, 9 warnings, 15.05 s. Inspection
  then found KatIA's earlier import. The complete-suite run started at that point was stopped;
  it is not counted as completed or green.
- Strengthening the regression to hold the actual import exposed the remaining KatIA path:
  **1 failed, 1 passed**, 2 warnings, 3.96 s, exit 1. Deferring that import completes the fix.
- Final focused group (new cases, original provider-wait test, provider rules, access checks
  and AI errors/scores): **45 passed**, 9 warnings, 13.39 s, exit 0.
- Corrected cold-process timeline: **1 passed**, 2 warnings, 5.40 s, exit 0.

```powershell
$env:ADMIN_PASSWORD = "testadmin123"
$env:PYTHONUTF8 = "1"
python -m pytest tests/api/test_ai_calls_off_event_loop.py tests/api/test_spec005_k1_providers.py tests/api/test_spec005_k2_katia.py tests/api/test_ai_errors_and_scores.py -q --tb=short
python -m pytest tests/ --ignore=tests/e2e -q --junitxml=tmp/qa-flows/latency-full-final.xml
```

The complete-suite result is recorded in the fixing PR's validation section. All tests run
locally on disposable SQLite; PostgreSQL skips are not reported as passes.

Black 24.3.0 reported **376 files unchanged**. Critical flake8 and `git diff --check` exited 0.
Traceability across all nine specs passed: **1284 pytest and 185 Playwright references**. The
new regression is added to existing FR-023; requirement text and delivery states are unchanged.
The three existing pending identity E5 rows remain in their open delivery.

As in the previous review, Windows collection used a temporary in-process runner adapter to
invoke the installed Playwright CLI directly, with dependencies reused through a junction.
No checker, frontend configuration, dependency, browser installation or migration changed.

Extracted measurement evidence: [cold, warm and corrected timelines](evidence/procedure-latency/timelines.txt).
Only timing lines were extracted; request payloads and credentials are not included.
