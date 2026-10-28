"""
Spec 002 D3 (FR-040, FR-041; US7): `scripts/db_sync_check.py` fails on what it claims to check.

Each case runs the script on copies of the two repositories, one of them edited the way a
one-engine change would edit it, and requires exit 1 with the object named. No database: this is
the static half of the parity check (the runtime half is tests/integration/test_spec002_d3_parity.py).
"""

import pathlib
import shutil
import subprocess
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[3]
_PERSISTENCE = _ROOT / "src" / "infrastructure" / "persistence"
_ANCHOR = "        self._check_courses_block_constraint(cursor)\n        self.init_db(cursor)\n"


def _copies(tmp_path):
    sqlite = tmp_path / "sqlite_repository.py"
    postgres = tmp_path / "postgres_repository.py"
    shutil.copy(_PERSISTENCE / "sqlite_repository.py", sqlite)
    shutil.copy(_PERSISTENCE / "postgres_repository.py", postgres)
    return sqlite, postgres


def _insert_after(path, anchor, text):
    source = path.read_text(encoding="utf-8")
    assert source.count(anchor) == 1, f"anchor not unique in {path.name}"
    path.write_text(source.replace(anchor, anchor + text), encoding="utf-8")


def _run(sqlite, postgres):
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/db_sync_check.py",
            "--sqlite",
            str(sqlite),
            "--postgres",
            str(postgres),
        ],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return proc.returncode, proc.stdout + proc.stderr


def test_the_repositories_pass():
    """The repositories as they are: every difference between them is an accepted one."""
    code, output = _run(
        _PERSISTENCE / "sqlite_repository.py", _PERSISTENCE / "postgres_repository.py"
    )
    assert code == 0, output


def test_a_column_added_to_one_engine_fails(tmp_path):
    """US7-AS1, FR-040: a column migrated on PostgreSQL only."""
    sqlite, postgres = _copies(tmp_path)
    _insert_after(
        postgres,
        _ANCHOR,
        '        self._add_column_if_not_exists(cursor, "users", "d3_probe", "TEXT")\n',
    )
    code, output = _run(sqlite, postgres)
    assert code == 1, output
    assert "users.d3_probe" in output


@pytest.mark.parametrize("unique", [False, True], ids=["index", "unique-index"])
def test_an_index_or_unique_index_on_one_engine_fails(tmp_path, unique):
    """US7-AS1, FR-040: an index, or a unique index, created on SQLite only."""
    sqlite, postgres = _copies(tmp_path)
    kind = "UNIQUE INDEX" if unique else "INDEX"
    _insert_after(
        sqlite,
        _ANCHOR,
        f'        cursor.execute("CREATE {kind} IF NOT EXISTS idx_d3_probe ON users(username)")\n',
    )
    code, output = _run(sqlite, postgres)
    assert code == 1, output
    assert "users(username)" in output


def test_a_parameter_after_a_tuple_default_differs_fails(tmp_path):
    """US7-AS2, FR-041: the parameter after a default containing parentheses — the old regex
    stopped at the first `)` and never compared it."""
    sqlite, postgres = _copies(tmp_path)
    anchor = "    def get_courses(self, block=None):\n"
    method = '    def d3_probe(self, fields=("a", "b"), {}=1):\n        return fields\n\n'
    for path, name in ((sqlite, "limit"), (postgres, "limit_rows")):
        source = path.read_text(encoding="utf-8")
        path.write_text(source.replace(anchor, method.format(name) + anchor, 1), encoding="utf-8")
    code, output = _run(sqlite, postgres)
    assert code == 1, output
    assert "d3_probe" in output


def test_a_stale_accepted_difference_fails(tmp_path):
    """The accepted differences stay exact: `storage_url` added to SQLite too makes its entry
    stale, and the check says so."""
    sqlite, postgres = _copies(tmp_path)
    _insert_after(
        sqlite,
        _ANCHOR,
        '        self._add_column_if_not_exists(cursor, "procedure_submissions", "storage_url", "TEXT")\n',
    )
    code, output = _run(sqlite, postgres)
    assert code == 1, output
    assert "procedure_submissions.storage_url" in output


@pytest.mark.parametrize("name", ["_COURSE_BLOCK_MAP", "_COURSE_NAME_MAP"])
def test_spec008_c_a_course_map_in_a_repository_fails(tmp_path, name):
    """Spec 008 FR-020 (plan-c.md O-C9): a course map back in one repository is a second copy of
    the catalogue; the check fails, naming the map and the catalogue module."""
    sqlite, postgres = _copies(tmp_path)
    anchor = '    BANK_DIR = os.path.join("items", "bank")\n'
    _insert_after(sqlite, anchor, f'    {name} = {{"geometria": "Colegio"}}\n')
    code, output = _run(sqlite, postgres)
    assert code == 1, output
    assert name in output and "src.domain.bank.catalogue" in output
