"""
Spec 002 D1: the schema version and the item-bank fingerprint (FR-015, FR-016).

A start reads the highest row of `schema_versions`; when it equals `SCHEMA_VERSION` the migration
issues no DDL. `MIGRATION_SOURCES_DIGEST` is the digest of every method that issues the schema's
DDL on both engines: `tests/unit/infrastructure/test_spec002_schema_version.py` recomputes it, so
changing that code without raising `SCHEMA_VERSION` (and recording the new digest) fails.

The item bank is synced only when its fingerprint differs from the last one recorded in
`bank_syncs`, so a start with an unchanged bank writes no item. `BANK_SYNC_FORMAT` is hashed into
the fingerprint: raising it makes every database resync once at its next start (spec 008 O-IL7).
"""

import glob
import hashlib
import inspect
import json
import os

SCHEMA_VERSION = 9  # 1: spec 002 D1; 2: SQLite idx_attempts_user_id (D3, N1); 3: spec 003 L4;
# 4: spec 005 K3 (katia_conversations, katia_messages);
# 5: spec 006 X2 (exam_responses.selected_option);
# 6: spec 008 T (items.subtopic, student_course_topic_elo_archive);
# 7: spec 004 E3 (users.access_until);
# 8: spec 009 I1 (student_identifications, student_imports, student_import_rows,
#    users.recovery_email, groups.institution, groups.grade);
# 9: spec 008 L (items.retired_at, items.bank_difficulty, item_difficulty_changes)
MIGRATION_SOURCES_DIGEST = "7701a4ba0dae9342840886904616d42cd1df955e15d901c0824ea80e3b9d6e1d"

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
    "_create_student_imports",
    "_add_item_life",
)

# Spec 008 L (O-IL7): what the sync writes changed (retired_at, bank_difficulty), so every database
# resyncs once after the deploy that carries it. Raise it again for any later change of the sync.
BANK_SYNC_FORMAT = 2

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
    """SHA-256 over the sync's format (spec 008 O-IL7), each bank file's relative path and content,
    and the course maps the sync applies with them (block and name: survey 008 B21); None without
    a bank."""
    files = bank_files(bank_dir)
    if not files:
        return None
    digest = hashlib.sha256()
    digest.update(f"bank-sync-format:{BANK_SYNC_FORMAT}".encode() + b"\0")
    if course_maps:
        digest.update(json.dumps(course_maps, sort_keys=True, ensure_ascii=False).encode() + b"\0")
    for path in files:
        digest.update(os.path.relpath(path, bank_dir).replace(os.sep, "/").encode() + b"\0")
        with open(path, "rb") as handle:
            digest.update(hashlib.sha256(handle.read()).digest())
    return digest.hexdigest()


def bank_item_ids(bank_dir: str) -> set[str]:
    """The ids of every item the bank files carry (spec 008 FR-034: the orphan repair keeps what
    the bank still names). A file that cannot be read raises: an unreadable file must never make
    its whole course look orphaned."""
    ids = set()
    for path in bank_files(bank_dir):
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError(f"{path}: a bank file is a JSON list of items")
        ids.update(str(item["id"]) for item in data if isinstance(item, dict) and "id" in item)
    return ids
