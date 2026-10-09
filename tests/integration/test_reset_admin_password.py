"""
scripts/reset_admin_password.py on both engines: it sets the password of one existing admin,
with the app's hashing, so the admin logs in with the new password and not with the old one; it
changes nothing for an unknown user or a non-admin; it never prints the password.
"""

import os
import sys
import uuid
from pathlib import Path

import pytest

from tests.integration.conftest import is_postgres

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import reset_admin_password as tool  # noqa: E402

OLD = "old-password-123"
NEW = "new-password-4567"


def _admin(repo) -> str:
    username = f"admin_{uuid.uuid4().hex[:10]}"
    ok, msg = repo.register_user(username, OLD, role="admin")
    assert ok, msg
    return username


def _run(repo, monkeypatch, username, password=NEW) -> int:
    monkeypatch.setenv("NEW_ADMIN_PASSWORD", password)
    if is_postgres(repo):
        monkeypatch.setenv("MIGRATION_DATABASE_URL", os.environ["POSTGRES_TEST_DATABASE_URL"])
        monkeypatch.setenv("DATABASE_SSLMODE", "disable")
        return tool.main(["--username", username])
    return tool.main(["--sqlite", repo.db_name, "--username", username])


def test_sets_the_new_password_of_an_admin(repo, monkeypatch, capsys):
    username = _admin(repo)
    assert _run(repo, monkeypatch, username) == 0
    out = capsys.readouterr()
    assert NEW not in out.out + out.err
    assert repo.login_user(username, NEW) is not None
    assert repo.login_user(username, OLD) is None


def test_unknown_user_changes_nothing(repo, monkeypatch, capsys):
    username = _admin(repo)
    assert _run(repo, monkeypatch, f"{username}_missing") == 1
    assert repo.login_user(username, OLD) is not None


def test_a_non_admin_is_refused(repo, monkeypatch):
    student = f"student_{uuid.uuid4().hex[:10]}"
    ok, msg = repo.register_user(student, OLD, role="student", education_level="colegio")
    assert ok, msg
    assert _run(repo, monkeypatch, student) == 1
    assert repo.login_user(student, OLD) is not None
    assert repo.login_user(student, NEW) is None


@pytest.mark.parametrize("weak", ["short-pass", " padded-password-123 "])
def test_a_weak_password_is_refused_before_connecting(repo, monkeypatch, capsys, weak):
    username = _admin(repo)
    assert _run(repo, monkeypatch, username, password=weak) == 2
    out = capsys.readouterr()
    assert weak.strip() not in out.out + out.err
    assert repo.login_user(username, OLD) is not None


def test_the_prompt_asks_twice():
    answers = iter([NEW, NEW + "x"])
    with pytest.raises(ValueError):
        tool.read_new_password(env={}, prompt=lambda _: next(answers))
    answers = iter([NEW, NEW])
    assert tool.read_new_password(env={}, prompt=lambda _: next(answers)) == NEW
