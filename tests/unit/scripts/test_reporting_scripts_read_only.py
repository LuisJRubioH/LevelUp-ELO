"""
scripts/monthly_metrics.py and scripts/train_calibrator.py only read attempts. Building a
repository runs the schema bootstrap unless RUN_MIGRATIONS=0: migrations, the bank sync and,
outside ENVIRONMENT=production, the demo and test-account seeds, all written to whatever
DATABASE_URL points at. The reports open the repository with RUN_MIGRATIONS=0.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import monthly_metrics  # noqa: E402
import train_calibrator  # noqa: E402


class _Repository:
    """Records what the process asked of the bootstrap when the repository was built."""

    run_migrations = []

    def __init__(self, *args, **kwargs):
        import os

        _Repository.run_migrations.append(os.environ.get("RUN_MIGRATIONS"))

    def get_all_attempts_for_calibration(self, **_kwargs):
        return []


@pytest.fixture
def repositories(monkeypatch):
    import src.infrastructure.persistence.postgres_repository as pg
    import src.infrastructure.persistence.sqlite_repository as sq

    _Repository.run_migrations = []
    monkeypatch.setattr(pg, "PostgresRepository", _Repository)
    monkeypatch.setattr(sq, "SQLiteRepository", _Repository)
    # Even a shell that asks for migrations gets none from a report (restored after the test).
    monkeypatch.setenv("RUN_MIGRATIONS", "1")
    return _Repository


@pytest.mark.parametrize("database_url", [None, "postgresql://user:pw@db.invalid:5432/postgres"])
def test_reports_never_bootstrap_the_schema(repositories, monkeypatch, database_url):
    if database_url:
        monkeypatch.setenv("DATABASE_URL", database_url)
    else:
        monkeypatch.delenv("DATABASE_URL", raising=False)

    monthly_metrics.cargar_repo()
    train_calibrator.cargar_datos()

    assert repositories.run_migrations == ["0", "0"]
