"""
scripts/reset_admin_password.py on both engines: it sets the password of one existing admin,
with the app's hashing, so the admin logs in with the new password and not with the old one; it
changes nothing for an unknown user or a non-admin; it never prints the password, nor the
database URL or its password when the connection fails.
"""

import io
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


def test_the_url_is_asked_hidden_when_the_environment_has_none():
    asked = []
    url = tool.database_url(
        env={}, prompt=lambda text: asked.append(text) or " postgresql://x ", interactive=True
    )
    assert url == "postgresql://x"
    assert asked == ["PostgreSQL URL (hidden): "]
    env = {"DATABASE_URL": "postgresql://y"}
    assert tool.database_url(env=env, prompt=pytest.fail, interactive=True) == "postgresql://y"
    assert tool.database_url(env={}, prompt=pytest.fail, interactive=False) is None


def test_with_no_url_and_no_terminal_it_stops_before_asking_the_password(monkeypatch):
    monkeypatch.delenv("MIGRATION_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(sys, "stdin", io.StringIO())
    monkeypatch.setattr(tool, "read_new_password", lambda: pytest.fail("asked for the password"))
    assert tool.main(["--username", "admin"]) == 2


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://u:pa%zzss@localhost:1/db",  # libpq quotes the bad token: the password
        "postgresql//u:pa%zzss@localhost/db",  # libpq quotes the whole malformed string
        "postgresql://u:pa%zzss@localhost:1/db?sslmode=disable&x",
        "postgresql://u:pa-zz-ss@localhost:1/db",  # valid, nothing listening
    ],
)
def test_a_connection_error_never_shows_the_url_or_its_password(monkeypatch, capsys, url):
    monkeypatch.setenv("MIGRATION_DATABASE_URL", url)
    monkeypatch.setenv("NEW_ADMIN_PASSWORD", NEW)
    monkeypatch.setenv("DATABASE_SSLMODE", "disable")
    assert tool.main(["--username", "admin"]) == 1
    err = capsys.readouterr().err
    assert "cannot connect" in err
    assert url not in err
    assert "pa%zzss" not in err and "pa-zz-ss" not in err


def test_a_server_message_quoting_the_password_is_redacted():
    url = "postgresql://u:s3cret-pass@db.example:5432/postgres"
    message = tool.connection_error(Exception('FATAL: bad value "s3cret-pass"'), url)
    assert "s3cret-pass" not in message
