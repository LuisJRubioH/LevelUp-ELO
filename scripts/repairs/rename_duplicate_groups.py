"""Fills groups.name_normalized and renames repeated group names (spec 002 FR-018).

The unique index on (teacher, normalised name) needs both; the migration stops naming this script
when a database lacks them. Each repeated (teacher, name) group but the oldest becomes
«<name>-DUP-<id>»: `python scripts/repairs/rename_duplicate_groups.py [--apply]`.
"""

from _repair import run

if __name__ == "__main__":
    run("repair_group_names", "groups renamed or given their normalised name", __doc__)
