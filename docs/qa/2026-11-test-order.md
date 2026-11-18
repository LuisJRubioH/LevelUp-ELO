# QA follow-up: enrollment test isolation

Started: 2026-11-16. Validation updated: 2026-11-17.
Branch: `codex/qa-test-order-review`, from `main` at `f50befa`.
This is a test-suite reliability correction. It changes no product behavior or requirement.
The before-fix order reproductions were recorded on Q15 head `17839d6`; the affected test was
unchanged in `f50befa`. The corrected test source is committed as `6948600`.

## Reproduced cause

`tests/api/test_student.py::TestEnroll::test_unenroll` used the session student's headers,
enrolled that student in `calculo_diferencial`, then removed the enrollment without restoring it.
The client, student token and headers in `tests/api/conftest.py` all have session scope. Later
AI tests assume that same student's enrollment for item `q21`.

The enrollment guard in `api/ai_target.py::require_enrolled_in_item` correctly refused those
requests with 403, before the mocked provider ran. This explains the AI failures in the
[exploratory Q15 parallel run](2026-11-ronda-2-q15.md#full-suite-execution).

Two local SQLite reproductions established the dependency before the correction:

| Order | Actual outcome | Exit |
|---|---|---|
| Unenroll, then one AI provider-error case | 1 failed, 1 passed; 7.50 s | 1 |
| Same two cases in reverse order | 2 passed; 10.09 s | 0 |
| Unenroll, then the three affected AI files | 13 failed, 4 passed; 9.41 s | 1 |
| Same 17 cases with unenroll last | 17 passed; 10.43 s | 0 |

The 13-case failure includes the 12 failures seen in the previous parallel suite plus the
free-procedure review case: without any other setup enrolling the shared student, that review
also correctly requires an enrollment.

## Correction

The existing unenrollment test now creates a unique university student using the repository's
established integration helpers and mints that student's token. It prepares the enrollment
directly as test data, verifies that it exists, calls the real HTTP DELETE and verifies that
the enrollment was removed. The setup no longer ignores a failed catalogue-enrollment POST.

The session account, enrollment guards, provider mocks, token lifetime and fixture scope are
unchanged. No rating is seeded or changed. Registration is test setup, not additional behavior
under test; creating the token directly also avoids auth rate-limit and cookie side effects.

## Verification

Both failing and control orders were repeated on the corrected source:

| Order | Actual outcome | Exit |
|---|---|---|
| Unenroll, then the three affected AI files | 17 passed; 14.40 s | 0 |
| Same 17 cases with unenroll last | 17 passed; 14.67 s | 0 |

```powershell
$env:ADMIN_PASSWORD = "testadmin123"
$env:PYTHONUTF8 = "1"
python -m pytest tests/api/test_student.py::TestEnroll::test_unenroll tests/api/test_ai_errors_and_scores.py tests/api/test_spec005_a_pins.py tests/api/test_ai_calls_off_event_loop.py -q --tb=short
python -m pytest tests/api/test_ai_errors_and_scores.py tests/api/test_spec005_a_pins.py tests/api/test_ai_calls_off_event_loop.py tests/api/test_student.py::TestEnroll::test_unenroll -q --tb=short
```

## Complete-suite outcomes and timing failures

The first full sequential and parallel sessions were launched concurrently on the local host.
Their actual results were:

| Mode | Actual outcome | Exit |
|---|---|---|
| Sequential | 1 failed, 2410 passed, 553 skipped; 125 warnings; 935.02 s | 1 |
| `-n 2 --dist=loadfile` | 1 failed, 2410 passed, 553 skipped; 129 warnings; 642.49 s | 1 |

The enrollment refusals no longer occurred. The sequential failure was
`test_ai_calls_off_event_loop.py::test_the_api_answers_while_a_procedure_is_reviewed[groq-review]`:
the health request waited 1.80085 s against a 1.0 s limit. The parallel failure was
`test_spec007_f_match_flow.py::test_spec007_the_server_closes_at_its_end_time_whatever_the_client_does[sqlite]`:
the observed finish was 1.733576 s after `ends_at`, against a 1.0 s limit.

Repeating only those two cases, without collecting the modified unenrollment test, yielded
**1 failed, 1 passed**, 6 warnings, 15.90 s (exit 1). League timing passed; the procedure review
latency still failed at 1.69488 s. Thus overlap alone has not been established as the cause of
both timing failures. Neither the timing tests, their tolerances nor product code were changed.

A further full sequential run and parallel run are executed one after the other. Their final
results are recorded in the PR's validation section. The earlier failed outcomes remain above.
All runs use local temporary SQLite. PostgreSQL is not configured locally; skipped cases are
not claimed as passed.
The exploratory parallel command requires pytest-xdist (locally installed version: 3.8.0);
the test correction itself adds no dependency or CI configuration change.

Black 24.3.0 (`--check --line-length=100 src/ tests/ scripts/`) reported **376 files unchanged**.
Critical flake8 (`src/ api/ tests/ scripts/ --max-line-length=100 --select=E9,F63,F7,F82`)
and `git diff --check` exited 0.

Traceability passed across all nine specs: **1283 pytest references, 185 Playwright references**.
The changed test file is cited by specs 001, 003 and 006; all three have no pending rows. The
three existing pending rows in identity delivery E5 remain allowed in that open delivery and
were not changed. This check collects references; it does not claim execution of skipped cases.

For Windows validation in this worktree, an in-process runner adapter replaced
`pnpm exec playwright` with `node <installed playwright/cli.js>` for collection. Dependencies
were reused through a local junction, avoiding pnpm's attempt to reinstall a linked directory.
No checker, frontend configuration, lockfile or browser installation changed.

## Procedure-latency follow-up

The remaining local procedure-review delay was subsequently traced to the cold provider
configuration import running on the API event loop, before the threaded provider call. The
[separate latency review](2026-11-procedure-latency.md) records the cold/cache control, SSL
profile, correction and deterministic responsiveness regressions.
