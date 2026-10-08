"""
scripts/check_traceability.py — every requirement and scenario maps to a test that exists, passes
and is not skipped (roadmap A-2; constitution § Governance, "Coverage and traceability").

For each specs/*/spec.md:

1. Definitions. Each functional requirement (a list item opening with **FR-nnn**) and each
   acceptance scenario (a numbered item opening with **USn-ASm**) is defined once.
2. § Traceability. One row per defined ID: no row for an undefined ID, no repeated row, no empty
   cell. Each reference is backticked and is a pytest node id (`path::test` or
   `path::Class::test`; without parameters it covers every parametrised case), a Playwright test
   (`frontend/e2e/file.spec.ts › title`, the title with or without its describe blocks), or
   `PENDING`.
3. `PENDING` is allowed except on the spec's code PR: a pull request from the spec's
   **Feature Branch** that changes anything outside specs/ and docs/ (its docs PR changes only
   those). CI passes the head branch and the changed files.
4. Every pytest reference matches a node of `pytest --collect-only`; every Playwright reference a
   test of `playwright test --list`.
5. With --run, the referenced tests run: each must pass and none may be skipped. pytest therefore
   needs both requirement files and POSTGRES_TEST_DATABASE_URL (two-engine tests take their
   PostgreSQL branch); Playwright runs with --retries=0.

Assertion adequacy stays a review item: a mapped test may assert only part of its requirement.

    python scripts/check_traceability.py                 # 1-4
    python scripts/check_traceability.py --run           # 1-5, as CI runs it
    python scripts/check_traceability.py --run --branch 002-x --changed-files changed.txt

Exit code 0 only if every check passed.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
E2E_DIR = "frontend/e2e/"
PW_SEP = " › "
DOC_ONLY_DIRS = ("specs/", "docs/")

_FR_DEF = re.compile(r"^\s*-\s+\*\*(FR-\d+[a-z]?)\*\*")
_AS_DEF = re.compile(r"^\s*\d+\.\s+\*\*(US\d+-AS\d+)\*\*")
_BRANCH = re.compile(r"^\*\*Feature Branch\*\*:\s*`([^`]+)`")
_ID = re.compile(r"^(FR-\d+[a-z]?|US\d+-AS\d+)$")
_TICKED = re.compile(r"`([^`]*)`")
_PYTEST_REF = re.compile(r"^(tests/[\w/.-]+\.py)((?:::\w+)+)(\[[^\]]*\])?$")


@dataclass
class Reference:
    kind: str  # "pytest", "playwright" or "pending"
    text: str
    path: str = ""  # pytest: the file; Playwright: the file relative to frontend/e2e
    target: str = ""  # pytest: "::Class::test[param]"; Playwright: the title


@dataclass
class Row:
    req: str
    line: int
    refs: list = field(default_factory=list)
    bad: list = field(default_factory=list)  # texts that are not a reference


@dataclass
class Spec:
    path: str
    feature_branch: str | None = None
    defined: dict = field(default_factory=dict)  # id -> line numbers of its definitions
    rows: list = field(default_factory=list)
    has_section: bool = False
    malformed_rows: list = field(default_factory=list)  # (line, first cell)


# ── 1-2. Parsing ────────────────────────────────────────────────────────────


def parse_reference(text):
    text = text.strip()
    if text == "PENDING":
        return Reference("pending", text)
    if text.startswith(E2E_DIR) and PW_SEP in text:
        file, title = text[len(E2E_DIR) :].split(PW_SEP, 1)
        if file.endswith((".spec.ts", ".test.ts")) and title.strip():
            return Reference("playwright", text, file, title.strip())
        return None
    match = _PYTEST_REF.match(text)
    if match:
        return Reference("pytest", text, match.group(1), match.group(2) + (match.group(3) or ""))
    return None


def parse_cell(cell):
    """References of one Test cell; texts that are not a reference go to `bad`."""
    refs, bad = [], []
    for part in re.split(r"<br\s*/?>", cell):
        part = part.strip()
        if not part:
            continue
        ticked = _TICKED.findall(part)
        loose = _TICKED.sub("", part).strip()
        if loose == "PENDING" and not ticked:
            refs.append(Reference("pending", loose))
            continue
        if loose or len(ticked) != 1:
            bad.append(part)
            continue
        ref = parse_reference(ticked[0])
        if ref is None:
            bad.append(part)
        else:
            refs.append(ref)
    return refs, bad


def parse_spec(text, path="spec.md"):
    spec = Spec(path=path)
    in_trace = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            in_trace = line.startswith("## Traceability")
            spec.has_section = spec.has_section or in_trace
            continue
        branch = _BRANCH.match(line)
        if branch and spec.feature_branch is None:
            spec.feature_branch = branch.group(1)
        if not in_trace:
            for pattern in (_FR_DEF, _AS_DEF):
                match = pattern.match(line)
                if match:
                    spec.defined.setdefault(match.group(1), []).append(number)
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        first = cells[0]
        if first == "Requirement / Scenario" or set(first) <= {"-", ":", " "}:
            continue
        if not _ID.match(first) or len(cells) != 2:
            spec.malformed_rows.append((number, first))
            continue
        refs, bad = parse_cell(cells[1])
        spec.rows.append(Row(first, number, refs, bad))
    return spec


# ── 2-3. Static checks ──────────────────────────────────────────────────────


def pending_rejected(spec, branch, changed_files):
    """True on the spec's code PR: its feature branch, changing something besides documents."""
    if not branch or branch != spec.feature_branch:
        return False
    return any(not path.startswith(DOC_ONLY_DIRS) for path in changed_files)


def static_errors(spec, reject_pending):
    errors = []
    if not spec.has_section:
        return [f"{spec.path}: no '## Traceability' section"]
    for req, lines in sorted(spec.defined.items()):
        if len(lines) > 1:
            errors.append(f"{spec.path}: {req} is defined {len(lines)} times (lines {lines})")
    for line, first in spec.malformed_rows:
        errors.append(f"{spec.path}:{line}: row '{first}' is not 'FR-… or USn-ASm | references'")
    seen = {}
    for row in spec.rows:
        where = f"{spec.path}:{row.line}: {row.req}"
        if row.req in seen:
            errors.append(f"{where} repeats the row at line {seen[row.req]}")
        seen.setdefault(row.req, row.line)
        if row.req not in spec.defined:
            errors.append(f"{where} names no requirement or scenario of this spec")
        for text in row.bad:
            errors.append(f"{where}: not a backticked test reference: {text}")
        if not row.refs and not row.bad:
            errors.append(f"{where} has no test")
        if reject_pending and any(r.kind == "pending" for r in row.refs):
            errors.append(f"{where} is PENDING on the spec's code PR")
    for req in sorted(set(spec.defined) - set(seen)):
        errors.append(f"{spec.path}: {req} has no row in § Traceability")
    return errors


# ── 4-5. Matching references to collected and executed tests ──────────────


def match_pytest(ref, nodes):
    """Collected node ids a pytest reference covers (all parametrised cases if it names none)."""
    wanted = ref.path + ref.target
    return sorted(
        n for n in nodes if n == wanted or (n.startswith(wanted + "[") and "[" not in ref.target)
    )


def junit_key(ref):
    """(classname, name) of a pytest reference as written to a JUnit report."""
    parts = ref.target.split("::")[1:]
    module = ref.path[: -len(".py")].replace("/", ".")
    return ".".join([module] + parts[:-1]), parts[-1]


def junit_outcomes(xml_text):
    """{(classname, name): passed | failed | skipped} from a pytest JUnit report."""
    outcomes = {}
    for case in ET.fromstring(xml_text).iter("testcase"):
        tags = {child.tag for child in case}
        if tags & {"failure", "error"}:
            outcome = "failed"
        elif "skipped" in tags:
            outcome = "skipped"
        else:
            outcome = "passed"
        outcomes[(case.get("classname"), case.get("name"))] = outcome
    return outcomes


def pytest_ref_outcomes(ref, outcomes):
    classname, name = junit_key(ref)
    return {
        n: o
        for (c, n), o in outcomes.items()
        if c == classname and (n == name or (n.startswith(name + "[") and "[" not in name))
    }


def flatten_playwright(report):
    """[(file, describe titles + title, run statuses)] from a Playwright JSON report."""
    tests = []

    def walk(suite, titles):
        for spec in suite.get("specs", []):
            statuses = [t.get("status") for t in spec.get("tests", [])]
            tests.append(
                (spec.get("file") or suite.get("file"), titles + [spec["title"]], statuses)
            )
        for child in suite.get("suites", []):
            walk(child, titles + [child["title"]])

    for top in report.get("suites", []):
        walk(top, [])
    return tests


def match_playwright(ref, tests):
    """Tests of the reference's file whose full title or own title equals the reference title."""
    return [
        t
        for t in tests
        if t[0] == ref.path and (PW_SEP.join(t[1]) == ref.target or t[1][-1] == ref.target)
    ]


# ── Runners ─────────────────────────────────────────────────────────────────


def run(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def pytest_collect(files):
    # pytest.ini adds -v; without it, -q prints one node id per collected test.
    proc = run(
        [sys.executable, "-m", "pytest", "-o", "addopts=", "--collect-only", "-q", "-rs"]
        + ["-p", "no:cacheprovider"]
        + sorted(files),
        ROOT,
    )
    lines = proc.stdout.splitlines()
    # With -q each collected test is one line: its node id (parameters may contain spaces).
    nodes = {line for line in lines if line.startswith("tests/") and "::" in line}
    notes = [line for line in lines if line.startswith(("ERROR", "SKIPPED"))]
    return nodes, notes


def pytest_run(node_ids, tmp):
    report = os.path.join(tmp, "junit.xml")
    proc = run(
        [sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider"]
        + [f"--junitxml={report}"]
        + sorted(node_ids),
        ROOT,
    )
    if not os.path.exists(report):
        return None, proc.stdout[-3000:] + proc.stderr[-3000:]
    with open(report, encoding="utf-8") as fh:
        return junit_outcomes(fh.read()), proc.stdout.splitlines()[-1:] if proc.stdout else []


def playwright_report(args, tmp, config=None):
    """Playwright JSON report of `playwright test <args>` (None plus the output if it failed)."""
    out = os.path.join(tmp, f"playwright-{len(os.listdir(tmp))}.json")
    env = dict(os.environ, PLAYWRIGHT_JSON_OUTPUT_FILE=out, PLAYWRIGHT_JSON_OUTPUT_NAME=out)
    cmd = ["pnpm", "exec", "playwright", "test", "--reporter=json"] + list(args)
    if config:
        cmd += ["--config", config]
    try:
        proc = run(cmd, FRONTEND, env)
    except FileNotFoundError:
        return None, "pnpm is not installed (Node >= 22.13 and pnpm are needed for frontend/e2e)"
    if not os.path.exists(out):
        return None, (proc.stdout + proc.stderr)[-3000:]
    with open(out, encoding="utf-8") as fh:
        return json.load(fh), ""


# ── Main ────────────────────────────────────────────────────────────────────


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", action="store_true", help="run the referenced tests (step 5)")
    ap.add_argument("--branch", default="", help="head branch of the pull request")
    ap.add_argument(
        "--changed-files", help="file listing the paths the pull request changes, one per line"
    )
    ap.add_argument("--playwright-config", help="Playwright config (default: frontend's)")
    ap.add_argument("specs", nargs="*", help="spec.md files (default: specs/*/spec.md)")
    args = ap.parse_args(argv)

    changed = []
    if args.changed_files:
        with open(args.changed_files, encoding="utf-8") as fh:
            changed = [line.strip() for line in fh if line.strip()]
    paths = args.specs or sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("specs/*/spec.md"))
    errors, refs = [], []
    for path in paths:
        spec = parse_spec((ROOT / path).read_text(encoding="utf-8"), path)
        reject = pending_rejected(spec, args.branch, changed)
        errors += static_errors(spec, reject)
        pending = [row.req for row in spec.rows if any(r.kind == "pending" for r in row.refs)]
        print(
            f"{path}: {len(spec.defined)} requirements and scenarios, {len(spec.rows)} rows,"
            f" PENDING {len(pending)} ({'rejected: code PR' if reject else 'allowed'})"
        )
        refs += [(path, row, ref) for row in spec.rows for ref in row.refs]

    py_refs = [(p, row, r) for p, row, r in refs if r.kind == "pytest"]
    pw_refs = [(p, row, r) for p, row, r in refs if r.kind == "playwright"]
    print(f"references: {len(py_refs)} pytest, {len(pw_refs)} Playwright")

    with tempfile.TemporaryDirectory() as tmp:
        if py_refs:
            nodes, notes = pytest_collect(
                {r.path for _, _, r in py_refs if (ROOT / r.path).exists()}
            )
            for path, row, ref in py_refs:
                if not (ROOT / ref.path).exists():
                    errors.append(f"{path}: {row.req}: no such file {ref.path}")
                elif not match_pytest(ref, nodes):
                    errors.append(f"{path}: {row.req}: not collected by pytest: {ref.text}")
            errors += [f"pytest collection: {note}" for note in notes]
        if pw_refs:
            files = sorted({E2E_DIR[len("frontend/") :] + r.path for _, _, r in pw_refs})
            listed, output = playwright_report(["--list"] + files, tmp, args.playwright_config)
            if listed is None:
                errors.append(f"playwright --list failed: {output}")
            else:
                tests = flatten_playwright(listed)
                for path, row, ref in pw_refs:
                    found = match_playwright(ref, tests)
                    if not found:
                        errors.append(f"{path}: {row.req}: not listed by Playwright: {ref.text}")
                    elif len(found) > 1:
                        errors.append(f"{path}: {row.req}: matches {len(found)} tests: {ref.text}")

        if args.run and not errors:
            errors += run_referenced(py_refs, pw_refs, tmp, args.playwright_config)
        elif args.run:
            print("referenced tests not run: fix the errors above first")

    for error in errors:
        print("FAIL " + error)
    print("RESULT: " + ("PASS" if not errors else f"FAIL ({len(errors)} problems)"))
    return 0 if not errors else 1


def run_referenced(py_refs, pw_refs, tmp, playwright_config):
    errors = []
    if py_refs:
        outcomes, tail = pytest_run({r.path + r.target for _, _, r in py_refs}, tmp)
        if outcomes is None:
            return [f"pytest did not produce a report: {tail}"]
        print(f"pytest: {len(outcomes)} referenced cases run; {' '.join(tail)}")
        for path, row, ref in py_refs:
            found = pytest_ref_outcomes(ref, outcomes)
            bad = {name: outcome for name, outcome in found.items() if outcome != "passed"}
            if not found:
                errors.append(f"{path}: {row.req}: did not run: {ref.text}")
            for name, outcome in sorted(bad.items()):
                errors.append(f"{path}: {row.req}: {outcome}: {ref.path}::{name}")
    if pw_refs:
        files = sorted({E2E_DIR[len("frontend/") :] + r.path for _, _, r in pw_refs})
        report, output = playwright_report(["--retries=0"] + files, tmp, playwright_config)
        if report is None:
            return errors + [f"playwright did not produce a report: {output}"]
        tests = flatten_playwright(report)
        print(f"playwright: {len(tests)} tests run in {len(files)} file(s)")
        for path, row, ref in pw_refs:
            for _, titles, statuses in match_playwright(ref, tests):
                if not statuses or any(s != "expected" for s in statuses):
                    errors.append(f"{path}: {row.req}: {statuses or 'not run'}: {ref.text}")
    return errors


if __name__ == "__main__":
    sys.exit(main())
