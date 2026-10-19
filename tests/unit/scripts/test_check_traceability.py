"""
Tests of scripts/check_traceability.py (roadmap A-2): spec parsing, the static checks, the
PENDING rule (which pull requests are a code change for a spec, whatever their branch) and how
references are matched to collected and executed tests. The collection and execution themselves
run in CI's traceability job against the real specs.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import check_traceability as ct  # noqa: E402

SPEC = """# Feature Specification: Example

**Feature Branch**: `009-example`

## Code Scope *(mandatory)*

- `src/domain/elo/`
- `api/routers/student.py` — the practice endpoints
- `frontend/src/pages/Student/*.tsx`

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


def test_parses_definitions_rows_and_code_scope():
    spec = ct.parse_spec(SPEC, "spec.md")

    assert [entry for _, entry in spec.scope] == [
        "src/domain/elo/",
        "api/routers/student.py",
        "frontend/src/pages/Student/*.tsx",
    ]
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
    assert len(errors) == 1
    assert errors[0].endswith("FR-001a is PENDING on a code change for this spec")


TRACKED = {
    "src/domain/elo/model.py",
    "api/routers/student.py",
    "frontend/src/pages/Student/Practice.tsx",
}


@pytest.mark.parametrize(
    "edit, expected",
    [
        (("## Code Scope *(mandatory)*", "## Scope"), "no '## Code Scope' section"),
        (
            (
                "- `src/domain/elo/`\n- `api/routers/student.py` — the practice endpoints\n"
                "- `frontend/src/pages/Student/*.tsx`\n",
                "The code of this spec.\n",
            ),
            "'## Code Scope' lists no path",
        ),
        (("- `src/domain/elo/`", "- `src/domain/elos/`"), "`src/domain/elos/` names no tracked"),
        (("api/routers/student.py`", "api/routers/students.py`"), "`api/routers/students.py`"),
    ],
)
def test_scope_errors(edit, expected):
    """Every spec declares the code it governs, and every entry names a tracked file — a typo
    would silently exempt that code from the PENDING rule."""
    assert ct.scope_errors(ct.parse_spec(SPEC, "specs/009-example/spec.md"), TRACKED) == []
    old, new = edit
    assert old in SPEC
    errors = ct.scope_errors(ct.parse_spec(SPEC.replace(old, new), "spec.md"), TRACKED)
    assert len(errors) == 1 and expected in errors[0], errors


@pytest.mark.parametrize(
    "entry, path, matches",
    [
        ("src/domain/elo/", "src/domain/elo/model.py", True),
        ("src/domain/elo/", "src/domain/elo_extra.py", False),
        ("api/routers/student.py", "api/routers/student.py", True),
        ("api/routers/student.py", "api/routers/student.pyc", False),
        ("frontend/src/pages/Student/*.tsx", "frontend/src/pages/Student/Practice.tsx", True),
        ("frontend/src/pages/Student/*.tsx", "frontend/src/pages/Student/lessons/A.tsx", True),
        ("frontend/src/pages/Student/*.tsx", "frontend/src/pages/Student/a.css", False),
    ],
)
def test_scope_matches(entry, path, matches):
    assert ct.scope_matches(entry, path) is matches


SPEC_DIR = "specs/009-example/"


@pytest.mark.parametrize(
    "changed, reasons",
    [
        # Documents only: the docs PR may say PENDING.
        ([SPEC_DIR + "spec.md", SPEC_DIR + "tasks.md", "docs/sdd/x.md", "README.md"], {}),
        # Code in the Code Scope, from any branch — spec.md need not change.
        (["src/domain/elo/model.py"], {"src/domain/elo/model.py": "Code Scope `src/domain/elo/`"}),
        (["api/routers/student.py"], {"api/routers/student.py": "Code Scope"}),
        (
            ["frontend/src/pages/Student/lessons/A.tsx"],
            {"frontend/src/pages/Student/lessons/A.tsx": "`frontend/src/pages/Student/*.tsx`"},
        ),
        # A test the spec cites is its code too.
        (["tests/unit/test_a.py"], {"tests/unit/test_a.py": "a test cited in § Traceability"}),
        (["frontend/e2e/a.spec.ts"], {"frontend/e2e/a.spec.ts": "a test cited"}),
        # Code outside the scope, alone: another area's PR does not block on this spec.
        (["scripts/other.py", "src/domain/learning/nodes/b06.py"], {}),
        # ... unless it changes this spec's files too.
        ([SPEC_DIR + "spec.md", "scripts/other.py"], {"scripts/other.py": "changed together"}),
        # A document inside the scope is not code; another spec's files do not count.
        (["src/domain/elo/NOTES.md", "specs/010-other/spec.md", "scripts/other.py"], {}),
    ],
)
def test_code_changes_do_not_depend_on_the_branch(changed, reasons):
    """Which changed paths make a pull request a code change for the spec. There is no branch
    input: `fix/whatever`, `001-elo-engine` or a fork's `main` are judged by their files."""
    spec = ct.parse_spec(SPEC, SPEC_DIR + "spec.md")
    found = ct.code_changes(spec, changed)
    assert set(found) == set(reasons), found
    for path, reason in reasons.items():
        assert reason in found[path], found


def test_main_rejects_pending_on_a_pr_from_an_arbitrary_branch(tmp_path, capsys):
    """End to end through main(): a PR from an arbitrary branch that changes a spec's code but
    not its spec.md fails while a row is PENDING; the same spec passes on a documents-only PR.
    The command line has no branch option at all."""
    spec_path = tmp_path / "spec.md"
    spec_path.write_text(
        "## Code Scope\n\n- `scripts/check_traceability.py`\n\n"
        "## Requirements\n\n- **FR-001** [CHANGE]: The system shall check.\n"
        "- **FR-002** [CHANGE]: The system shall report.\n\n"
        "## Traceability\n\n| Requirement / Scenario | Test |\n|---|---|\n"
        "| FR-001 | `tests/unit/scripts/test_check_traceability.py::test_scope_matches` |\n"
        "| FR-002 | `PENDING` |\n",
        encoding="utf-8",
    )
    code_pr = tmp_path / "code.txt"
    code_pr.write_text("scripts/check_traceability.py\n", encoding="utf-8")
    docs_pr = tmp_path / "docs.txt"
    docs_pr.write_text("docs/sdd/roadmap.md\nREADME.md\n", encoding="utf-8")

    assert ct.main(["--changed-files", str(code_pr), str(spec_path)]) == 1
    out = capsys.readouterr().out
    assert "code change: scripts/check_traceability.py (Code Scope" in out
    assert "FR-002 is PENDING on a code change for this spec" in out
    assert "RESULT: FAIL (1 problems)" in out

    assert ct.main(["--changed-files", str(docs_pr), str(spec_path)]) == 0
    assert "PENDING 1 (allowed)" in capsys.readouterr().out

    with pytest.raises(SystemExit):
        ct.main(["--branch", "001-elo-engine", str(spec_path)])


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
    tracked = ct.tracked_files()
    for path in paths:
        spec = ct.parse_spec(path.read_text(encoding="utf-8"), str(path))
        assert spec.defined and len(spec.rows) == len(spec.defined)
        assert ct.static_errors(spec, reject_pending=False) == []
        assert ct.scope_errors(spec, tracked) == []


# ── Constitution 1.1.0 (decision P13): format-independent definitions and deliveries ─────────


@pytest.mark.parametrize(
    "line, req",
    [
        ("- FR-002 [CHANGE]: The system shall log.", "FR-002"),
        ("- *FR-002* [CHANGE]: The system shall log.", "FR-002"),
        ("- `FR-002` [CHANGE]: The system shall log.", "FR-002"),
        ("* __FR-002__ [CHANGE]: The system shall log.", "FR-002"),
        ("FR-002: The system shall log.", "FR-002"),
        ("### FR-002 — The system shall log", "FR-002"),
        ("| FR-002 | The system shall log. |", "FR-002"),
        ("3. US1-AS3 — Given a student, When they log in, Then it logs.", "US1-AS3"),
        ("3. *US1-AS3*: Given a student, When they log in, Then it logs.", "US1-AS3"),
    ],
)
def test_a_requirement_needs_a_row_whatever_its_formatting(line, req):
    """Removing the bold (or using any other Markdown shape) never takes a requirement out of
    the check: it is recognised as a definition and must have its own row."""
    text = SPEC.replace("## Traceability", f"{line}\n\n## Traceability")
    assert req in ct.parse_spec(text).defined
    errors = errors_of(text)
    assert any(f"{req} has no row" in error for error in errors), errors


@pytest.mark.parametrize(
    "line",
    [
        "FR-002 The system shall log.",  # no punctuation after the ID
        "The system shall log, as FR-002 says.",
        "> FR-002 [CHANGE]: The system shall log.",  # a quote is not a definition
    ],
)
def test_an_id_mentioned_but_never_defined_fails(line):
    """A requirement written in a shape the checker does not read as a definition is still
    caught: its ID is mentioned and defined nowhere."""
    errors = errors_of(SPEC.replace("## Traceability", f"{line}\n\n## Traceability"))
    assert any("FR-002 is mentioned" in error and "defined nowhere" in error for error in errors)


def test_other_specs_ids_and_evidence_tables_are_not_mentions():
    """Another spec's ID, qualified by its number, and the appendix's evidence rows are
    references, not this spec's requirements."""
    text = SPEC.replace(
        "## Traceability",
        "- The catalogue rule stays as spec 001 FR-028m and spec 001, FR-028l state.\n\n"
        "## Traceability",
    ).replace("| FR-001 | read at `src/x.py:1` |", "| FR-777 | read at `src/x.py:1` |")
    assert errors_of(text) == []
    assert "FR-028m" not in ct.parse_spec(text).mentioned


def test_ids_mentioned_in_prose_count_once_defined():
    """Mentions of defined IDs — ranges, lists, wrapped lines — are fine and never definitions."""
    text = SPEC.replace(
        "## Requirements *(mandatory)*",
        "## Clarifications\n\n- Q: Why? → A: see FR-001 and FR-001a, and\n"
        "  FR-001 … FR-001a again (US1-AS1 … AS2).\n\n## Requirements *(mandatory)*",
    )
    spec = ct.parse_spec(text)
    assert sorted(spec.defined) == ["FR-001", "FR-001a", "US1-AS1", "US1-AS2"]
    assert all(len(lines) == 1 for lines in spec.defined.values())
    assert errors_of(text) == []


SPEC_D = """# Feature Specification: Delivered in steps

## Code Scope *(mandatory)*

- `scripts/check_traceability.py`

## Deliveries *(mandatory for this spec)*

| Delivery | Content | State |
|---|---|---|
| **E1** | Closed sign-up | closed |
| **E2** | Display name | in progress |
| **E3** | Import | planned |

## Requirements *(mandatory)*

- **FR-001** [CHANGE]: The system shall refuse self-registration.
- **FR-002** [CHANGE]: The system shall show the display name.
- **FR-003** [CHANGE]: The system shall import a class.

## Traceability *(mandatory)*

| Requirement / Scenario | Delivery | Test |
|---|---|---|
| FR-001 | E1 | `tests/unit/scripts/test_check_traceability.py::test_scope_matches` |
| FR-002 | E2 | `PENDING` |
| FR-003 | E3 | `PENDING` |
"""


def errors_d(text=SPEC_D, reject_pending=False):
    return ct.static_errors(ct.parse_spec(text, "spec.md"), reject_pending)


def test_deliveries_are_parsed():
    spec = ct.parse_spec(SPEC_D)
    assert spec.has_deliveries and spec.delivery_column
    assert {name: state for name, (state, _) in spec.deliveries.items()} == {
        "E1": "closed",
        "E2": "in progress",
        "E3": "planned",
    }
    assert [(row.req, row.delivery) for row in spec.rows] == [
        ("FR-001", "E1"),
        ("FR-002", "E2"),
        ("FR-003", "E3"),
    ]
    assert ct.open_deliveries(spec) == {"E2", "E3"}


def test_pending_in_open_deliveries_is_allowed_even_on_a_code_change():
    """A requirement planned for E3 may stay PENDING while E2 is delivered (decision P13)."""
    assert errors_d() == []
    assert errors_d(reject_pending=True) == []


@pytest.mark.parametrize("reject_pending", [False, True])
def test_pending_in_a_closed_delivery_always_fails(reject_pending):
    """No requirement of a closed delivery may stay PENDING — not on a docs PR either."""
    text = SPEC_D.replace(
        "| **E2** | Display name | in progress |", "| **E2** | Display name | closed |"
    )
    errors = errors_d(text, reject_pending)
    assert len(errors) == 1, errors
    assert errors[0].endswith("FR-002 is PENDING in closed delivery E2"), errors


@pytest.mark.parametrize(
    "edit, expected",
    [
        (("| FR-003 | E3 |", "| FR-003 | E9 |"), "FR-003 names no declared delivery: 'E9'"),
        (("| FR-003 | E3 |", "| FR-003 |  |"), "FR-003 names no declared delivery: ''"),
        (("| planned |", "| someday |"), "delivery E3 has state 'someday'"),
        (("| **E3** | Import |", "| **E2** | Import |"), "delivery E2 is declared twice"),
        (("| Delivery | Content | State |", "| Step | Content | Status |"), "has no table with"),
        (
            ("| Requirement / Scenario | Delivery | Test |", "| Requirement / Scenario | Test |"),
            "needs a Delivery column",
        ),
        (("| FR-001 | E1 | `tests", "| FR-001 | `tests"), "row 'FR-001' is not"),
    ],
)
def test_delivery_errors(edit, expected):
    old, new = edit
    assert old in SPEC_D
    errors = errors_d(SPEC_D.replace(old, new))
    assert any(expected in error for error in errors), errors


def test_a_delivery_column_needs_declared_deliveries():
    text = SPEC_D.replace("## Deliveries *(mandatory for this spec)*", "## Steps")
    errors = errors_d(text)
    assert any("has a Delivery column but no '## Deliveries'" in error for error in errors)


def test_main_applies_the_delivery_rule_end_to_end(tmp_path, capsys):
    """Through main(): a code PR passes while only open deliveries are PENDING, and fails once
    a delivery with a PENDING row is marked closed."""
    spec_path = tmp_path / "spec.md"
    spec_path.write_text(SPEC_D, encoding="utf-8")
    code_pr = tmp_path / "code.txt"
    code_pr.write_text("scripts/check_traceability.py\n", encoding="utf-8")

    assert ct.main(["--changed-files", str(code_pr), str(spec_path)]) == 0
    out = capsys.readouterr().out
    assert "PENDING 2 (by delivery: E2 1, E3 1; deliveries E1 closed" in out

    spec_path.write_text(SPEC_D.replace("| planned |", "| closed |"), encoding="utf-8")
    assert ct.main(["--changed-files", str(code_pr), str(spec_path)]) == 1
    assert "FR-003 is PENDING in closed delivery E3" in capsys.readouterr().out
