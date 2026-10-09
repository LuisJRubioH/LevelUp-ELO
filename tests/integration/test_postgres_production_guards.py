"""Guardas de producción ejecutadas contra PostgreSQL real y desechable."""

import os
import io
import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from PIL import Image


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_TEST_DATABASE_URL"),
    reason="Requiere POSTGRES_TEST_DATABASE_URL hacia una base desechable.",
)


@pytest.fixture(scope="module")
def postgres_context():
    os.environ["DATABASE_URL"] = os.environ["POSTGRES_TEST_DATABASE_URL"]
    os.environ["DATABASE_SSLMODE"] = "disable"
    os.environ["TESTING"] = "1"
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    os.environ.setdefault("ADMIN_PASSWORD", "postgres-audit-admin")

    import api.dependencies as deps
    from api.main import app
    from src.infrastructure.persistence.postgres_repository import PostgresRepository
    from starlette.testclient import TestClient

    repo = PostgresRepository()
    suffix = uuid.uuid4().hex[:12]
    conn = repo.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved, active) "
                "VALUES (%s, %s, 'teacher', 1, 1) RETURNING id",
                (f"pg_teacher_a_{suffix}", "unused"),
            )
            teacher_a = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, approved, active) "
                "VALUES (%s, %s, 'teacher', 1, 1) RETURNING id",
                (f"pg_teacher_b_{suffix}", "unused"),
            )
            teacher_b = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO groups (name, name_normalized, course_id, teacher_id) "
                "VALUES (%s, %s, 'calculo_diferencial', %s) RETURNING id",
                (f"PG audit {suffix}", f"pg audit {suffix}", teacher_a),
            )
            group_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, group_id, active) "
                "VALUES (%s, %s, 'student', %s, 1) RETURNING id",
                (f"pg_student_{suffix}", "unused", group_id),
            )
            student_id = cursor.fetchone()[0]
        conn.commit()
    finally:
        repo.put_connection(conn)
    # The group's student practises its course: an enrolment is required (spec 001 FR-037).
    repo.enroll_user(student_id, "calculo_diferencial", group_id)

    deps._repo_instance = repo
    client = TestClient(app, base_url="https://postgres-audit.local", raise_server_exceptions=False)
    context = {
        "repo": repo,
        "client": client,
        "teacher_a": teacher_a,
        "teacher_b": teacher_b,
        "group_id": group_id,
        "student_id": student_id,
        "a_headers": {
            "Authorization": "Bearer "
            + deps.create_access_token(teacher_a, f"pg_teacher_a_{suffix}", "teacher")
        },
        "b_headers": {
            "Authorization": "Bearer "
            + deps.create_access_token(teacher_b, f"pg_teacher_b_{suffix}", "teacher")
        },
        "student_headers": {
            "Authorization": "Bearer "
            + deps.create_access_token(student_id, f"pg_student_{suffix}", "student")
        },
    }
    yield context
    client.close()
    deps._repo_instance = None
    repo._pool.closeall()


def _topic_rating(repo, user_id, topic):
    """The (calculo_diferencial, topic) rating of the course × topic store (spec 001)."""
    rows = repo.get_course_topic_ratings(user_id, course_id="calculo_diferencial")
    return next(r["elo"] for r in rows if r["topic"] == topic)


def test_postgres_permissions_diagnostic_and_canonical_answer(postgres_context):
    from src.application.services.rating_read_service import RatingReadService

    ctx = postgres_context
    repo = ctx["repo"]
    client = ctx["client"]
    student_id = ctx["student_id"]
    group_id = ctx["group_id"]

    for suffix in ("", "/elo-history", "/katia-history", "/ranking"):
        assert (
            client.get(
                f"/api/teacher/student/{student_id}{suffix}", headers=ctx["b_headers"]
            ).status_code
            == 404
        )
        assert (
            client.get(
                f"/api/teacher/student/{student_id}{suffix}", headers=ctx["a_headers"]
            ).status_code
            == 200
        )

    original_code = repo.generate_group_invite_code(group_id)
    assert (
        client.post(
            f"/api/teacher/groups/{group_id}/invite-code", headers=ctx["b_headers"]
        ).status_code
        == 404
    )
    assert repo.get_group_by_invite_code(original_code)["group_id"] == group_id

    item = repo.get_items_from_db(course_id="calculo_diferencial")[0]
    repo.save_diagnostic(student_id, "calculo_diferencial", 1234, 75, "{}")
    repo.set_topic_rating_baseline(student_id, "calculo_diferencial", item["topic"], 1234)
    ratings = RatingReadService(repo)
    assert _topic_rating(repo, student_id, item["topic"]) == 1234
    assert ratings.course_rating_of(student_id, "calculo_diferencial") == 1234

    response = client.post(
        "/api/student/answer",
        headers=ctx["student_headers"],
        json={
            "item_id": item["id"],
            "item_data": {**item, "difficulty": 1777},
            "selected_option": item["correct_option"],
            "time_taken": 30,
        },
    )
    assert response.status_code == 200
    conn = repo.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT item_id, difficulty, topic FROM attempts "
                "WHERE user_id=%s ORDER BY id DESC LIMIT 1",
                (student_id,),
            )
            saved = cursor.fetchone()
    finally:
        repo.put_connection(conn)
    # attempts.difficulty is INTEGER on PostgreSQL (REAL on SQLite): history keeps the canonical
    # difficulty rounded to a whole number, never the client's 1777 (roadmap follow-up F-3).
    assert saved == (item["id"], round(item["difficulty"]), item["topic"])
    persisted_before_redo = _topic_rating(repo, student_id, item["topic"])
    wrong = next(option for option in item["options"] if option != item["correct_option"])
    redone = client.post(
        "/api/student/diagnostic/calculo_diferencial/submit",
        headers=ctx["student_headers"],
        json={"answers": [{"item_id": item["id"], "selected_option": wrong}]},
    )
    assert redone.status_code == 200
    assert _topic_rating(repo, student_id, item["topic"]) == persisted_before_redo


def test_postgres_atomic_procedure_and_assignment_guards(postgres_context):
    ctx = postgres_context
    repo = ctx["repo"]
    client = ctx["client"]
    item = repo.get_items_from_db(course_id="calculo_diferencial")[0]
    conn = repo.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO procedure_submissions "
                "(student_id, item_id, item_content, image_data, status, ai_proposed_score) "
                "VALUES (%s, %s, %s, %s, 'PENDING_TEACHER_VALIDATION', 99) RETURNING id",
                (ctx["student_id"], item["id"], item["content"], b"postgres audit"),
            )
            submission_id = cursor.fetchone()[0]
        conn.commit()
    finally:
        repo.put_connection(conn)

    assert (
        client.post(
            "/api/teacher/procedures/grade",
            headers=ctx["b_headers"],
            json={"submission_id": submission_id, "teacher_score": 0},
        ).status_code
        == 404
    )
    graded = client.post(
        "/api/teacher/procedures/grade",
        headers=ctx["a_headers"],
        json={"submission_id": submission_id, "teacher_score": 80},
    )
    assert graded.status_code == 200
    assert graded.json()["elo_delta"] == 6
    assert (
        client.post(
            "/api/teacher/procedures/grade",
            headers=ctx["a_headers"],
            json={"submission_id": submission_id, "teacher_score": 50},
        ).status_code
        == 404
    )

    own_template = repo.create_exam_template(
        ctx["teacher_b"], "calculo_diferencial", "PG own", 10, [item["id"]]
    )
    victim_template = repo.create_exam_template(
        ctx["teacher_a"], "calculo_diferencial", "PG victim", 10, [item["id"]]
    )
    victim_assignment = repo.create_exam_assignment(victim_template, ctx["group_id"])
    assert (
        client.delete(
            f"/api/teacher/exam-templates/{own_template}/assignments/{victim_assignment}",
            headers=ctx["b_headers"],
        ).status_code
        == 404
    )
    assert [row["id"] for row in repo.list_assignments_for_template(victim_template)] == [
        victim_assignment
    ]
    own_assignment = repo.create_exam_assignment(own_template, ctx["group_id"])
    assert (
        client.delete(
            f"/api/teacher/exam-templates/{own_template}/assignments/{own_assignment}",
            headers=ctx["b_headers"],
        ).status_code
        == 204
    )


def test_postgres_cookie_refresh_and_immediate_account_revocation(postgres_context):
    ctx = postgres_context
    client = ctx["client"]
    username = f"pg_revocation_{uuid.uuid4().hex[:10]}"
    assert (
        client.post(
            "/api/auth/register",
            json={"username": username, "password": "password123", "role": "student"},
        ).status_code
        == 201
    )
    login = client.post("/api/auth/login", json={"username": username, "password": "password123"})
    assert login.status_code == 200
    cookie = next(c for c in client.cookies.jar if c.name == "levelup_refresh")
    assert cookie.path == "/api/auth"
    assert client.post("/api/auth/refresh").status_code == 200

    conn = ctx["repo"].get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET active=0 WHERE id=%s", (login.json()["user_id"],))
        conn.commit()
    finally:
        ctx["repo"].put_connection(conn)
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}
    assert client.get("/api/student/courses", headers=headers).status_code == 401
    assert client.post("/api/auth/refresh").status_code == 401


def test_postgres_concurrent_answer_retry_has_one_effect(postgres_context):
    ctx = postgres_context
    repo = ctx["repo"]
    item = repo.get_items_from_db(course_id="calculo_diferencial")[1]
    key = "pg-concurrent-" + uuid.uuid4().hex
    body = {
        "item_id": item["id"],
        "selected_option": item["correct_option"],
        "time_taken": 30,
    }

    def submit():
        return ctx["client"].post(
            "/api/student/answer",
            headers={**ctx["student_headers"], "Idempotency-Key": key},
            json=body,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: submit(), range(2)))
    assert [response.status_code for response in responses] == [200, 200]
    elo_results = {
        (response.json()["elo_before"], response.json()["elo_after"]) for response in responses
    }
    assert len(elo_results) == 1

    conn = repo.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM attempts WHERE user_id=%s AND request_id=%s",
                (ctx["student_id"], key),
            )
            assert cursor.fetchone()[0] == 1
    finally:
        repo.put_connection(conn)

    wrong = next(option for option in item["options"] if option != item["correct_option"])
    conflict = ctx["client"].post(
        "/api/student/answer",
        headers={**ctx["student_headers"], "Idempotency-Key": key},
        json={**body, "selected_option": wrong},
    )
    assert conflict.status_code == 409


def test_postgres_exam_window_composition_and_retry_integrity(postgres_context):
    ctx = postgres_context
    repo = ctx["repo"]
    client = ctx["client"]
    item = repo.get_items_from_db(course_id="calculo_diferencial")[0]

    future_template = repo.create_exam_template(
        ctx["teacher_a"], "calculo_diferencial", "PG future", 10, [item["id"]]
    )
    repo.create_exam_assignment(
        future_template, ctx["group_id"], "2099-01-01T00:00:00", "2099-01-02T00:00:00"
    )
    denied = client.post(
        "/api/student/exam/start",
        headers=ctx["student_headers"],
        json={"course_id": "calculo_diferencial", "template_id": future_template},
    )
    assert denied.status_code == 404

    start = client.post(
        "/api/student/exam/start",
        headers=ctx["student_headers"],
        json={"course_id": "calculo_diferencial", "n_questions": 1},
    )
    assert start.status_code == 200
    run = start.json()
    answer = {
        "item_id": run["items"][0]["id"],
        "selected_option": run["items"][0]["options"][0],
    }
    duplicate = client.post(
        "/api/student/exam/submit",
        headers=ctx["student_headers"],
        json={"session_id": run["session_id"], "answers": [answer, answer]},
    )
    assert duplicate.status_code == 400

    payload = {"session_id": run["session_id"], "answers": [answer]}
    first = client.post("/api/student/exam/submit", headers=ctx["student_headers"], json=payload)
    replay = client.post("/api/student/exam/submit", headers=ctx["student_headers"], json=payload)
    assert first.status_code == replay.status_code == 200
    assert first.json() == replay.json()

    conn = repo.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM active_exam_sessions WHERE id=%s AND submitted_at IS NOT NULL",
                (run["session_id"],),
            )
            assert cursor.fetchone()[0] == 1
    finally:
        repo.put_connection(conn)


def test_postgres_procedure_review_token_and_antiplagiarism(postgres_context):
    import api.dependencies as dependencies

    ctx = postgres_context
    repo = ctx["repo"]
    output = io.BytesIO()
    Image.new("RGB", (2, 2), (25, 90, 150)).save(output, format="PNG")
    image = output.getvalue()
    item_id = "pg-upload-" + uuid.uuid4().hex
    token = dependencies.create_procedure_review_token(
        ctx["student_id"], item_id, hashlib.sha256(image).hexdigest(), 87, "PG verified"
    )
    saved = ctx["client"].post(
        "/api/student/procedure",
        headers=ctx["student_headers"],
        data={"item_id": item_id, "analysis_token": token},
        files={"file": ("work.png", image, "image/png")},
    )
    assert saved.status_code == 200
    assert saved.json()["submission_id"] > 0
    submission = repo.get_student_submission(ctx["student_id"], item_id)
    assert submission["ai_proposed_score"] == 87
    assert submission["ai_feedback"] == "PG verified"

    conn = repo.get_connection()
    try:
        with conn.cursor() as cursor:
            username = "pg_upload_other_" + uuid.uuid4().hex[:10]
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, active) "
                "VALUES (%s, %s, 'student', 1) RETURNING id",
                (username, "unused"),
            )
            other_id = cursor.fetchone()[0]
        conn.commit()
    finally:
        repo.put_connection(conn)
    other_headers = {
        "Authorization": "Bearer " + dependencies.create_access_token(other_id, username, "student")
    }
    duplicate = ctx["client"].post(
        "/api/student/procedure",
        headers=other_headers,
        data={"item_id": item_id},
        files={"file": ("copy.png", image, "image/png")},
    )
    assert duplicate.status_code == 409
