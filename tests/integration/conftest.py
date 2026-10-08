"""
Two-engine fixtures and helpers for integration tests (spec 001, task T001).

`repo` runs every test that uses it against SQLite always and against PostgreSQL when
POSTGRES_TEST_DATABASE_URL points at a disposable local database (tests/conftest.py refuses
any non-local host). PostgreSQL persists between tests, so helpers create uniquely named rows.

Pins read ratings only through `rating_of` and answer only through `answer`, so moving the
rating store (spec 001) re-points these two helpers without changing any asserted number.
"""

import json
import os
import uuid

import pytest

_PG_URL = os.environ.get("POSTGRES_TEST_DATABASE_URL")


# ── Engine-agnostic SQL ──────────────────────────────────────────────────────


def is_postgres(repo) -> bool:
    return hasattr(repo, "put_connection")


def sql(repo, statement: str, params=()) -> list:
    """Run SQL on either engine; `?` placeholders are translated to `%s` for PostgreSQL."""
    conn = repo.get_connection()
    try:
        if is_postgres(repo):
            with conn.cursor() as cursor:
                cursor.execute(statement.replace("?", "%s"), params)
                rows = cursor.fetchall() if cursor.description else []
        else:
            cursor = conn.execute(statement, params)
            rows = cursor.fetchall() if cursor.description else []
        conn.commit()
        return rows
    finally:
        if is_postgres(repo):
            repo.put_connection(conn)
        else:
            conn.close()


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def _postgres_repo():
    if not _PG_URL:
        pytest.skip("Requiere POSTGRES_TEST_DATABASE_URL hacia una base desechable.")
    os.environ["DATABASE_URL"] = _PG_URL
    os.environ.setdefault("DATABASE_SSLMODE", "disable")
    os.environ.setdefault("ADMIN_PASSWORD", "postgres-audit-admin")

    from src.infrastructure.persistence.postgres_repository import PostgresRepository

    return PostgresRepository()


@pytest.fixture(params=["sqlite", "postgres"])
def repo(request, tmp_path):
    """The same test body against both engines."""
    if request.param == "postgres":
        return request.getfixturevalue("_postgres_repo")

    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    return SQLiteRepository(db_name=str(tmp_path / "elo_source.db"))


def _unique(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def make_student(repo, education_level="colegio", grade=None) -> int:
    username = _unique("elo_source")
    ok, msg = repo.register_user(
        username, "password123", "student", education_level=education_level, grade=grade
    )
    assert ok, msg
    return sql(repo, "SELECT id FROM users WHERE username = ?", (username,))[0][0]


@pytest.fixture
def student(repo) -> int:
    """A new student per test — PostgreSQL persists between tests."""
    return make_student(repo)


@pytest.fixture
def client(repo):
    """The FastAPI app on this test's engine (no lifespan: the `repo` is already bootstrapped)."""
    import api.dependencies as deps
    from api.main import app
    from starlette.testclient import TestClient

    previous = deps._repo_instance
    deps._repo_instance = repo
    test_client = TestClient(app, base_url="https://spec001.local", raise_server_exceptions=False)
    yield test_client
    test_client.close()
    deps._repo_instance = previous


def headers_for(repo, user_id) -> dict:
    from api.dependencies import create_access_token

    row = sql(repo, "SELECT username, role FROM users WHERE id = ?", (user_id,))[0]
    return {"Authorization": "Bearer " + create_access_token(user_id, row[0], row[1])}


# ── Seeding helpers ──────────────────────────────────────────────────────────


def make_course(
    repo, topics, block="Colegio", name=None, difficulty=1000.0, items_per_topic=1, id_suffix=""
):
    """Create a course with `items_per_topic` items per topic. Returns (course_id, {topic: [ids]}).

    `id_suffix` carries what the real catalogue encodes in ids, e.g. `_semillero_6`.
    """
    course_id = _unique("spec001_course") + id_suffix
    sql(
        repo,
        "INSERT INTO courses (id, name, block, description) VALUES (?, ?, ?, '')",
        (course_id, name or course_id, block),
    )
    items = {}
    for topic in topics:
        for n in range(items_per_topic):
            item_id = _unique("spec001_item")
            sql(
                repo,
                "INSERT INTO items (id, topic, content, options, correct_option, difficulty,"
                " rating_deviation, course_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item_id,
                    topic,
                    f"{topic} #{n}",
                    json.dumps(["A", "B", "C", "D"]),
                    "A",
                    float(difficulty),
                    350.0,
                    course_id,
                ),
            )
            items.setdefault(topic, []).append(item_id)
    return course_id, items


def make_teacher(repo) -> int:
    username = _unique("spec001_teacher")
    ok, msg = repo.register_user(username, "password123", "teacher")
    assert ok, msg
    return sql(repo, "SELECT id FROM users WHERE username = ?", (username,))[0][0]


def make_group(repo, teacher_id, course_id=None) -> int:
    ok, msg, group_id = repo.create_group(_unique("spec001_group"), teacher_id, course_id)
    assert ok, msg
    return group_id


def enroll(repo, user_id, course_id, group_id=None) -> None:
    repo.enroll_user(user_id, course_id, group_id)


# ── The two helpers every pin goes through ───────────────────────────────────


def answer(repo, user_id, item_id, correct=True, seconds=20.0):
    """Answer an item through the real StudentService path. Returns (is_correct, result)."""
    from src.application.services.student_service import StudentService

    item = repo.get_item_by_id(item_id)
    option = (
        item["correct_option"]
        if correct
        else next(o for o in item["options"] if o != item["correct_option"])
    )
    return StudentService(repository=repo).process_answer(user_id, item, option, "", seconds)


def rating_of(repo, user_id, course_id, topic):
    """The student's current rating for (course, topic), or None (student_course_topic_elo)."""
    rows = sql(
        repo,
        "SELECT current_elo FROM student_course_topic_elo"
        " WHERE user_id = ? AND course_id = ? AND topic = ?",
        (user_id, course_id, topic),
    )
    return float(rows[0][0]) if rows else None


def set_rating(repo, user_id, course_id, topic, elo, rd=350.0, origin="diagnostic"):
    """Seed a student's (course, topic) rating in student_course_topic_elo."""
    sql(
        repo,
        "INSERT INTO student_course_topic_elo (user_id, course_id, topic, current_elo, rd, origin)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, course_id, topic, elo, rd, origin),
    )
