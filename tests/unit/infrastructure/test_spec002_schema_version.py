"""
Spec 002 FR-015 (task T011): the schema version stays honest.

`MIGRATION_SOURCES_DIGEST` is the digest of the code that issues the schema's DDL on both
engines, recorded together with `SCHEMA_VERSION`. Changing that code without raising the version
would let a database at the "current" version skip a migration it never ran; this test catches it.
"""

from src.infrastructure.persistence.schema_version import (
    MIGRATION_SOURCES_DIGEST,
    SCHEMA_VERSION,
    migration_sources_digest,
)


def test_migration_code_changes_raise_the_version():
    current = migration_sources_digest()
    assert current == MIGRATION_SOURCES_DIGEST, (
        "The migration code changed: raise SCHEMA_VERSION (now %d) and record the new digest, "
        "MIGRATION_SOURCES_DIGEST = %r, in src/infrastructure/persistence/schema_version.py"
        % (SCHEMA_VERSION, current)
    )
