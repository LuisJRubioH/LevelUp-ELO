"""
Spec 002 D1: the schema version and the item-bank fingerprint (FR-015, FR-016).

A start reads the highest row of `schema_versions`; when it equals `SCHEMA_VERSION` the migration
issues no DDL. `MIGRATION_SOURCES_DIGEST` is the digest of every method that issues the schema's
DDL on both engines: `tests/unit/infrastructure/test_spec002_schema_version.py` recomputes it, so
changing that code without raising `SCHEMA_VERSION` (and recording the new digest) fails.

The item bank is synced only when its fingerprint differs from the last one recorded in
`bank_syncs`, so a start with an unchanged bank writes no item.
"""

import glob
import hashlib
import inspect
import json
import os

SCHEMA_VERSION = 6  # 1: spec 002 D1; 2: SQLite idx_attempts_user_id (D3, N1); 3: spec 003 L4;
# 4: spec 005 K3 (katia_conversations, katia_messages);
# 5: spec 006 X2 (exam_responses.selected_option);
# 6: spec 008 T (items.subtopic, student_course_topic_elo_archive)
MIGRATION_SOURCES_DIGEST = "288b4e275a6051a6df679408b4784a5a00c8ea152c2ce8a8960490a63432a0c0"

# Every method that issues DDL, or decides whether the migration may run, on both repositories.
_MIGRATION_METHODS = (
    "init_db",
    "_add_column_if_not_exists",
    "_migrate_db",
    "_run_migration",
    "_migrate_procedure_block7",
    "_backfill_procedure_contributions",
    "_ensure_procedure_pair_index",
    "_check_courses_block_constraint",
    "_check_group_names",
    "_make_image_data_nullable",
    "_create_lesson_history",
    "_create_katia_conversations",
    "_add_exam_selected_option",
    "_add_item_subtopics",
)

REPAIR_GROUPS = "scripts/repairs/rename_duplicate_groups.py"


class MigrationFailed(RuntimeError):
    """A migration step failed; its transaction was rolled back, so nothing of it committed."""

    def __init__(self, step: str, cause: BaseException):
        super().__init__(
            f"Migration step '{step}' failed and committed nothing: "
            f"{type(cause).__name__}: {cause}"
        )
        self.step = step


class MigrationNeedsRepair(RuntimeError):
    """The migration needs data only a repair script produces (spec 002 FR-018)."""

    def __init__(self, script: str, rows: int, what: str):
        super().__init__(
            f"Migration stopped, nothing committed: {rows} {what}. "
            f"Run `python {script}` (dry run), then with --apply, and start again."
        )
        self.script = script


def migration_sources_digest() -> str:
    """SHA-256 of the source of every migration method of both repositories."""
    from src.infrastructure.persistence.postgres_repository import PostgresRepository
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    digest = hashlib.sha256()
    for cls in (PostgresRepository, SQLiteRepository):
        for name in _MIGRATION_METHODS:
            digest.update(f"{cls.__name__}.{name}\n".encode())
            digest.update(inspect.getsource(getattr(cls, name)).encode())
    return digest.hexdigest()


def bank_files(bank_dir: str) -> list[str]:
    """The files `sync_items_from_bank_folder` reads, in its order."""
    files = sorted(glob.glob(os.path.join(bank_dir, "*.json")))
    return files + sorted(glob.glob(os.path.join(bank_dir, "semillero", "*.json")))


def bank_fingerprint(bank_dir: str, course_maps: dict | None = None) -> str | None:
    """SHA-256 over each bank file's relative path and content, and over the course maps the sync
    applies with them (block and name: survey 008 B21); None without a bank."""
    files = bank_files(bank_dir)
    if not files:
        return None
    digest = hashlib.sha256()
    if course_maps:
        digest.update(json.dumps(course_maps, sort_keys=True, ensure_ascii=False).encode() + b"\0")
    for path in files:
        digest.update(os.path.relpath(path, bank_dir).replace(os.sep, "/").encode() + b"\0")
        with open(path, "rb") as handle:
            digest.update(hashlib.sha256(handle.read()).digest())
    return digest.hexdigest()
