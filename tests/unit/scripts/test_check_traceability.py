"""
Tests of scripts/check_traceability.py (roadmap A-2): spec parsing, the static checks, the
PENDING rule and how references are matched to collected and executed tests. The collection and
execution themselves run in CI's traceability job against the real specs.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import check_traceability as ct  # noqa: E402

SPEC = """# Feature Specification: Example

**Feature Branch**: `009-example`

## User Scenarios & Testing *(mandatory)*

**Acceptance Scenarios**:

1. **US1-AS1** — **Given** a student, **When** they answer, **Then** it moves.
2. **US1-AS2** — **Given** a student, **When** they wait, **Then** nothing moves.

## Requirements *(mandatory)*

- **FR-001** [AS-IS]: The system shall move the rating.
- **FR-001a** [CHANGE]: The system shall keep the history.

## Traceability *(mandatory)*

| Requirement / Scenario | Test |
|---|---|
| US1-AS1 | `tests/unit/test_a.py::test_moves`<br>`frontend/e2e/a.spec.ts › Moves (US1-AS1)` |
| US1-AS2 | `tests/unit/test_a.py::TestWait::test_nothing` |
| FR-001 | `tests/unit/test_a.py::test_moves` |
| FR-001a | `PENDING` |

## Appendix — As-is evidence

| FR-001 | read at `src/x.py:1` |
"""


def errors_of(text, reject_pending=False):
    return ct.static_errors(ct.parse_spec(text, "spec.md"), reject_pending)


def test_parses_definitions_rows_and_feature_branch():
    spec = ct.parse_spec(SPEC, "spec.md")

    assert spec.feature_branch == "009-example"
    assert sorted(spec.defined) == ["FR-001", "FR-001a", "US1-AS1", "US1-AS2"]
    assert [row.req for row in spec.rows] == ["US1-AS1", "US1-AS2", "FR-001", "FR-001a"]
    kinds = [[ref.kind for ref in row.refs] for row in spec.rows]
    assert kinds == [["pytest", "playwright"], ["pytest"], ["pytest"], ["pending"]]
    playwright = spec.rows[0].refs[1]
    assert (playwright.path, playwright.target) == ("a.spec.ts", "Moves (US1-AS1)")


def test_a_complete_table_has_no_static_error():
    assert errors_of(SPEC) == []


def test_tables_outside_traceability_are_ignored():
    """The appendix also has an FR-001 row; it is evidence, not a second traceability row."""
    assert len([row for row in ct.parse_spec(SPEC).rows if row.req == "FR-001"]) == 1


@pytest.mark.parametrize(
    "edit, expected",
    [
        (("| FR-001 | `tests/unit/test_a.py::test_moves` |\n", ""), "FR-001 has no row"),
        (("- **FR-001a**", "- **FR-001**"), "FR-001 is defined 2 times"),
        (("| FR-001a | `PENDING` |", "| FR-002 | `PENDING` |"), "FR-002 names no requirement"),
        (
            ("| FR-001a | `PENDING` |", "| FR-001a | `PENDING` |\n| FR-001 | `PENDING` |"),
            "FR-001 repeats the row",
        ),
        (("| FR-001a | `PENDING` |", "| FR-001a |  |"), "FR-001a has no test"),
        (
            ("`tests/unit/test_a.py::TestWait::test_nothing`", "tests/unit/test_a.py::test_x"),
            "not a backticked test reference",
        ),
        (("`tests/unit/test_a.py::TestWait::test_nothing`", "`see FR-001`"), "not a backticked"),
        (("| FR-001a | `PENDING` |", "| FR 1 | `PENDING` |"), "row 'FR 1' is not"),
        (("## Traceability *(mandatory)*", "## Mapping"), "no '## Traceability' section"),
    ],
)
def test_static_errors(edit, expected):
    old, new = edit
    assert old in SPEC
    errors = errors_of(SPEC.replace(old, new))
    assert any(expected in error for error in errors), errors


def test_pending_is_rejected_only_when_asked():
    assert errors_of(SPEC) == []
    errors = errors_of(SPEC, reject_pending=True)
    assert len(errors) == 1 and errors[0].endswith("FR-001a is PENDING on the spec's code PR")


@pytest.mark.parametrize(
    "branch, changed, rejected",
    [
        ("009-example", ["specs/009-example/spec.md", "specs/009-example/tasks.md"], False),
        ("009-example", ["specs/009-example/spec.md", "docs/sdd/example-survey.md"], False),
        ("009-example", ["specs/009-example/spec.md", "src/domain/x.py"], True),
        ("009-example", ["frontend/src/App.tsx"], True),
        ("ci/a2-traceability", ["scripts/check_traceability.py"], False),
        ("", ["src/domain/x.py"], False),
    ],
)
def test_pending_rule_is_the_specs_code_pr(branch, changed, rejected):
    """Docs PR (only specs/ and docs/) may say PENDING; the spec's code PR may not; other PRs
    do not block on a spec whose code PR has not landed yet."""
    spec = ct.parse_spec(SPEC)
    assert ct.pending_rejected(spec, branch, changed) is rejected


NODES = {
    "tests/unit/test_a.py::test_moves",
    "tests/unit/test_a.py::test_moves_fast",
    "tests/unit/test_a.py::TestWait::test_nothing",
    "tests/integration/test_b.py::test_store[sqlite]",
    "tests/integration/test_b.py::test_store[postgres]",
    "tests/integration/test_b.py::test_label[postgres-999.4-Plata II]",
}


@pytest.mark.parametrize(
    "text, matched",
    [
        ("tests/unit/test_a.py::test_moves", ["tests/unit/test_a.py::test_moves"]),
        (
            "tests/unit/test_a.py::TestWait::test_nothing",
            ["tests/unit/test_a.py::TestWait::test_nothing"],
        ),
        (
            "tests/integration/test_b.py::test_store",
            [
                "tests/integration/test_b.py::test_store[postgres]",
                "tests/integration/test_b.py::test_store[sqlite]",
            ],
        ),
        (
            "tests/integration/test_b.py::test_store[sqlite]",
            ["tests/integration/test_b.py::test_store[sqlite]"],
        ),
        (
            "tests/integration/test_b.py::test_label",
            ["tests/integration/test_b.py::test_label[postgres-999.4-Plata II]"],
        ),
        ("tests/unit/test_a.py::test_move", []),
        ("tests/unit/test_a.py::test_nothing", []),
    ],
)
def test_pytest_reference_matching(text, matched):
    """A reference covers its own node and, without parameters, every parametrised case — never
    a test whose name merely starts the same way."""
    assert ct.match_pytest(ct.parse_reference(text), NODES) == matched


JUNIT = """<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest">
<testcase classname="tests.unit.test_a" name="test_moves" />
<testcase classname="tests.unit.test_a.TestWait" name="test_nothing" />
<testcase classname="tests.integration.test_b" name="test_store[sqlite]" />
<testcase classname="tests.integration.test_b" name="test_store[postgres]">
  <skipped message="no PG"/></testcase>
<testcase classname="tests.integration.test_b" name="test_broken"><failure message="x"/></testcase>
<testcase classname="tests.integration.test_b" name="test_setup"><error message="x"/></testcase>
</testsuite></testsuites>"""


@pytest.mark.parametrize(
    "text, expected",
    [
        ("tests/unit/test_a.py::test_moves", {"test_moves": "passed"}),
        ("tests/unit/test_a.py::TestWait::test_nothing", {"test_nothing": "passed"}),
        (
            "tests/integration/test_b.py::test_store",
            {"test_store[sqlite]": "passed", "test_store[postgres]": "skipped"},
        ),
        ("tests/integration/test_b.py::test_store[sqlite]", {"test_store[sqlite]": "passed"}),
        ("tests/integration/test_b.py::test_broken", {"test_broken": "failed"}),
        ("tests/integration/test_b.py::test_setup", {"test_setup": "failed"}),
        ("tests/integration/test_b.py::test_missing", {}),
    ],
)
def test_junit_outcomes_per_reference(text, expected):
    """A skipped parametrised case (e.g. the PostgreSQL branch without a database) is reported,
    so a reference only counts when every one of its cases passed."""
    outcomes = ct.junit_outcomes(JUNIT)
    assert ct.pytest_ref_outcomes(ct.parse_reference(text), outcomes) == expected


REPORT = {
    "suites": [
        {
            "title": "a.spec.ts",
            "file": "a.spec.ts",
            "specs": [
                {"title": "Top level", "file": "a.spec.ts", "tests": [{"status": "expected"}]}
            ],
            "suites": [
                {
                    "title": "Ratings",
                    "file": "a.spec.ts",
                    "specs": [
                        {
                            "title": "Moves (US1-AS1)",
                            "file": "a.spec.ts",
                            "tests": [{"status": "expected"}],
                        },
                        {"title": "Waits", "file": "a.spec.ts", "tests": [{"status": "skipped"}]},
                    ],
                }
            ],
        }
    ]
}


@pytest.mark.parametrize(
    "text, statuses",
    [
        ("frontend/e2e/a.spec.ts › Moves (US1-AS1)", [["expected"]]),
        ("frontend/e2e/a.spec.ts › Ratings › Moves (US1-AS1)", [["expected"]]),
        ("frontend/e2e/a.spec.ts › Top level", [["expected"]]),
        ("frontend/e2e/a.spec.ts › Waits", [["skipped"]]),
        ("frontend/e2e/b.spec.ts › Moves (US1-AS1)", []),
        ("frontend/e2e/a.spec.ts › Moves", []),
    ],
)
def test_playwright_reference_matching(text, statuses):
    """The title matches with or without its describe blocks, in the reference's own file."""
    tests = ct.flatten_playwright(REPORT)
    assert [t[2] for t in ct.match_playwright(ct.parse_reference(text), tests)] == statuses


@pytest.mark.parametrize(
    "text",
    [
        "tests/unit/test_a.py",
        "src/domain/x.py::test_y",
        "frontend/e2e/a.spec.ts",
        "frontend/src/a.spec.ts › Title",
        "pytest tests/unit",
    ],
)
def test_unrecognised_references(text):
    assert ct.parse_reference(text) is None


def test_the_repository_specs_pass_the_static_checks():
    """Every spec in the repository parses into a complete table (collection and execution are
    checked by CI's traceability job)."""
    paths = sorted(ROOT.glob("specs/*/spec.md"))
    assert paths
    for path in paths:
        spec = ct.parse_spec(path.read_text(encoding="utf-8"), str(path))
        assert spec.defined and len(spec.rows) == len(spec.defined)
        assert ct.static_errors(spec, reject_pending=False) == []
