"""
Spec 002 D3: the differences between the two engines' schemas that are accepted, and why.

Both halves of the parity check read this list:

- `scripts/db_sync_check.py` parses the migration code of each repository (tables, columns,
  indexes);
- `tests/integration/test_spec002_d3_parity.py` reads what each database reports after a
  bootstrap (and column type families as well).

Either fails on a difference missing from this list, and on an entry the engines no longer differ
in (FR-040). Adding an entry is a decision: its reason names who took it.
"""

from collections import Counter
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Difference:
    kind: str  # "table", "column", "index" or "type"
    key: str  # "table", "table.column" or "table(col, col)" (+ " UNIQUE")
    side: str  # the engine that has it: "sqlite" or "postgres"; "both" for a type
    reason: str


ACCEPTED = (
    Difference(
        "column",
        "procedure_submissions.storage_url",
        "postgres",
        "SQLite has no Supabase Storage; files stay in the row (spec 002 N1, AGENTS R9).",
    ),
    Difference(
        "index",
        "groups(teacher_id)",
        "postgres",
        "PostgreSQL indexes groups(teacher_id) twice (idx_groups_teacher, idx_groups_teacher_id); "
        "dropping one is not additive (R8) — kept and documented (spec 002 N7).",
    ),
    Difference(
        "type",
        "active_exam_sessions.expires_at",
        "both",
        "TEXT on SQLite, TIMESTAMP on PostgreSQL: SQLite has no timestamp type (spec 002 § "
        "Clarifications, P2/P3).",
    ),
    Difference(
        "type",
        "exam_assignments.starts_at",
        "both",
        "TEXT on SQLite, TIMESTAMP on PostgreSQL (as above).",
    ),
    Difference(
        "type",
        "exam_assignments.ends_at",
        "both",
        "TEXT on SQLite, TIMESTAMP on PostgreSQL (as above).",
    ),
    Difference(
        "type",
        "users.access_until",
        "both",
        "TEXT (YYYY-MM-DD) on SQLite, DATE on PostgreSQL: SQLite has no date type; both engines "
        "return the same text (spec 004 E3, FR-046; as spec 002 § Clarifications, P2/P3).",
    ),
    Difference(
        "type",
        "exam_templates.archived",
        "both",
        "INTEGER on SQLite, BOOLEAN on PostgreSQL: SQLite has no boolean type.",
    ),
    Difference(
        "type",
        "student_course_topic_elo.approximate",
        "both",
        "INTEGER on SQLite, BOOLEAN on PostgreSQL (as above).",
    ),
)


def type_family(declared: str) -> str:
    """The family a declared column type belongs to, the same on both engines."""
    t = (declared or "").upper()
    if "INT" in t or t in ("SERIAL", "BIGSERIAL"):
        return "int"
    if "DOUBLE" in t or "REAL" in t or "FLOAT" in t or "NUMERIC" in t:
        return "float"
    if "TIME" in t or "DATE" in t:
        return "time"
    if "BOOL" in t:
        return "bool"
    if "BYTEA" in t or "BLOB" in t:
        return "bytes"
    return "text"


@dataclass
class Catalogue:
    """Tables with their columns (and declared types), and indexes counted by shape."""

    tables: dict = field(default_factory=dict)
    indexes: Counter = field(default_factory=Counter)

    def add_table(self, table: str) -> None:
        self.tables.setdefault(table, {})

    def add_column(self, table: str, column: str, declared: str = "") -> None:
        self.tables.setdefault(table, {})[column] = declared

    def add_index(self, table: str, columns, unique: bool) -> None:
        self.indexes[(table, tuple(columns), bool(unique))] += 1


def _index_key(table, columns, unique) -> str:
    return f"{table}({', '.join(columns)})" + (" UNIQUE" if unique else "")


def differences(sqlite: Catalogue, postgres: Catalogue, types: bool) -> set:
    """Every (kind, key, side) the two catalogues differ in."""
    found = set()
    for side, mine, other in (("sqlite", sqlite, postgres), ("postgres", postgres, sqlite)):
        for table, columns in mine.tables.items():
            if table not in other.tables:
                found.add(("table", table, side))
                continue
            for column in columns:
                if column not in other.tables[table]:
                    found.add(("column", f"{table}.{column}", side))
        for shape, count in mine.indexes.items():
            if count > other.indexes.get(shape, 0):
                found.add(("index", _index_key(*shape), side))
    if types:
        for table, columns in sqlite.tables.items():
            for column, declared in columns.items():
                theirs = postgres.tables.get(table, {}).get(column)
                if theirs is not None and type_family(declared) != type_family(theirs):
                    found.add(("type", f"{table}.{column}", "both"))
    return found


def unexplained(sqlite: Catalogue, postgres: Catalogue, runtime: bool) -> list[str]:
    """The differences that are not accepted, and the accepted ones that no longer exist.

    `runtime=False` (the static check, which reads code) compares tables, columns and indexes;
    `runtime=True` (what the databases report) adds column type families.
    """
    found = differences(sqlite, postgres, types=runtime)
    accepted = {(d.kind, d.key, d.side) for d in ACCEPTED if runtime or d.kind != "type"}
    problems = [
        f"{kind} {key}: only on {side}" if side != "both" else f"{kind} {key}: differs"
        for kind, key, side in sorted(found - accepted)
    ]
    problems += [
        f"accepted difference no longer exists: {kind} {key} ({side})"
        for kind, key, side in sorted(accepted - found)
    ]
    return problems
