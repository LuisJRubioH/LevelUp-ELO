"""
The `courses.block` CHECK constraint: read it, never rewrite it (spec 001 FR-028n, AGENTS R8).

Neither engine can widen a CHECK in place: PostgreSQL needs DROP + ADD CONSTRAINT and SQLite a
table rebuild, and neither is additive. So the migration only reads the constraint. When it
accepts the four blocks the code writes, nothing happens and any extra value stays; when it does
not, the migration stops here, before changing anything, and the repair is a reviewed change of
its own (docs/sdd/f1-semillero-survey.md § 4.3).
"""

import re

from src.domain.entities import COURSE_BLOCKS

_BLOCK_IN = re.compile(r"\bblock\s+IN\s*\(([^)]*)\)", re.IGNORECASE)
_BLOCK_ANY = re.compile(r"\bblock\s*=\s*ANY\s*\(\s*ARRAY\s*\[([^\]]*)\]", re.IGNORECASE)
_LITERAL = re.compile(r"'((?:[^']|'')*)'")


class CourseBlockConstraintError(RuntimeError):
    """The stored constraint rejects a block the code writes; the migration stops."""


def allowed_blocks(check_sql: str):
    """The values the `block` CHECKs in `check_sql` allow (all must hold), or None if there is
    no CHECK at all. SQLite gives its CREATE TABLE text; PostgreSQL its constraint definitions."""
    clauses = _BLOCK_IN.findall(check_sql) + _BLOCK_ANY.findall(check_sql)
    if not clauses:
        if re.search(r"\bCHECK\b", check_sql, re.IGNORECASE):
            raise CourseBlockConstraintError(
                "cannot read the courses.block constraint; the migration changed nothing: "
                f"{check_sql!r}. See docs/sdd/f1-semillero-survey.md § 4.3."
            )
        return None
    allowed = None
    for clause in clauses:
        values = {v.replace("''", "'") for v in _LITERAL.findall(clause)}
        allowed = values if allowed is None else allowed & values
    return allowed


def require_course_blocks(check_sql: str) -> None:
    """Raise CourseBlockConstraintError naming the blocks the constraint does not accept."""
    allowed = allowed_blocks(check_sql)
    if allowed is None:
        return
    missing = [block for block in COURSE_BLOCKS if block not in allowed]
    if missing:
        names = ", ".join(f"'{block}'" for block in missing)
        raise CourseBlockConstraintError(
            f"courses.block constraint does not accept {names}; the migration stopped before "
            "changing the constraint or the courses table. Repairing it is a reviewed change "
            "with a backup: see docs/sdd/f1-semillero-survey.md § 4.3."
        )
