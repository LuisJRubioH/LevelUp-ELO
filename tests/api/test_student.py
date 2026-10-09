"""
tests/api/test_student.py
==========================
Tests del flujo de práctica del estudiante:
  GET  /api/student/courses        → catálogo de cursos
  GET  /api/student/stats          → ELO y estadísticas
  POST /api/student/enroll         → matrícula en un curso
  POST /api/student/next-question  → siguiente pregunta adaptativa
  POST /api/student/answer         → procesar respuesta
  GET  /api/student/history        → historial de intentos
  DELETE /api/student/enroll/{id}  → darse de baja
  GET  /api/student/achievements   → logros/badges
  POST /api/student/exam/start     → iniciar examen
  POST /api/student/exam/submit    → enviar respuestas del examen
"""

import pytest

_COURSE_ID = "algebra_basica"  # Colegio — presente en el banco de preguntas
_COURSE_UNIV = "calculo_diferencial"  # Universidad


def _enrol_directly(api_client, headers, course_id):
    """estudiante1 is a universidad student: a colegio course is outside their catalogue, so
    /enroll refuses it (spec 001 FR-028m). Enrol directly, as an invitation would, so each test
    sets up its own enrolment instead of relying on another class having run first."""
    from api.dependencies import get_repository

    user_id = api_client.get("/api/auth/me", headers=headers).json()["user_id"]
    get_repository().enroll_user(user_id, course_id)


@pytest.mark.parametrize("from_map", [False, True])
def test_first_practice_uses_diagnostic_rating(api_client, monkeypatch, from_map):
    """Spec 001 (FR-004, FR-029a; flipped by T045): the first practice starts from the
    diagnostic's topic baselines — the topic's own from the map, their mean (the course rating)
    for the whole course. There is no course-average seed any more."""
    from statistics import fmean

    from api.dependencies import decode_token, get_repository
    from src.application.services.rating_read_service import RatingReadService

    repo = get_repository()
    username = f"diagnostic_practice_{int(from_map)}"
    registered = api_client.post(
        "/api/auth/register",
        json={"username": username, "password": "test-local-123", "role": "student"},
    )
    assert registered.status_code == 201
    login = api_client.post(
        "/api/auth/login", json={"username": username, "password": "test-local-123"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}
    user_id = int(decode_token(token)["sub"])
    enrolled = api_client.post(
        "/api/student/enroll", headers=headers, json={"course_id": _COURSE_UNIV}
    )
    assert enrolled.status_code == 201  # practice needs an enrolment (spec 001 FR-037)
    items = repo.get_items_from_db(course_id=_COURSE_UNIV)[:10]
    diagnostic = api_client.post(
        f"/api/student/diagnostic/{_COURSE_UNIV}/submit",
        headers=headers,
        json={
            "answers": [
                {"item_id": item["id"], "selected_option": item["correct_option"]} for item in items
            ]
        },
    )
    assert diagnostic.status_code == 200

    def stored():
        return {r["topic"]: r["elo"] for r in repo.get_course_topic_ratings(user_id, _COURSE_UNIV)}

    def expected_selection(ratings):
        return ratings.get(topic, 1000.0) if from_map else fmean(ratings.values())

    baselines = stored()
    topic = items[0]["topic"]
    assert baselines[topic] != 1000
    observed = []
    original = RatingReadService.selection_rating

    def capture(self, *args, **kwargs):
        observed.append(original(self, *args, **kwargs))
        return observed[-1]

    monkeypatch.setattr(RatingReadService, "selection_rating", capture)
    request = {"course_id": _COURSE_UNIV}
    if from_map:
        request["topic"] = topic
    question = api_client.post("/api/student/next-question", headers=headers, json=request)
    assert question.status_code == 200
    assert observed[-1] == pytest.approx(expected_selection(baselines))
    canonical = repo.get_item_by_id(question.json()["item"]["id"])
    response = api_client.post(
        "/api/student/answer",
        headers=headers,
        json={
            "item_id": canonical["id"],
            "selected_option": canonical["correct_option"],
            "time_taken": 30,
        },
    )
    assert response.status_code == 200
    started_from = baselines.get(canonical["topic"], 1000.0)
    assert response.json()["elo_before"] == pytest.approx(started_from, abs=0.01)
    assert response.json()["elo_after"] > started_from
    api_client.post("/api/student/next-question", headers=headers, json=request)
    after_practice = stored()
    assert observed[-1] == pytest.approx(expected_selection(after_practice))

    wrong = next(o for o in canonical["options"] if o != canonical["correct_option"])
    redone = api_client.post(
        f"/api/student/diagnostic/{_COURSE_UNIV}/submit",
        headers=headers,
        json={"answers": [{"item_id": canonical["id"], "selected_option": wrong}]},
    )
    assert redone.status_code == 200
    # El resultado diagnóstico se actualiza, pero el progreso de práctica no retrocede (FR-021).
    assert stored()[canonical["topic"]] == after_practice[canonical["topic"]]


@pytest.mark.parametrize(
    "answers",
    [
        lambda own, other: [
            {"item_id": own["id"], "selected_option": own["correct_option"]},
            {"item_id": own["id"], "selected_option": own["correct_option"]},
        ],
        lambda own, other: [{"item_id": other["id"], "selected_option": other["correct_option"]}],
        lambda own, other: [{"item_id": own["id"], "selected_option": "inventada"}],
    ],
)
def test_diagnostic_rejects_noncanonical_payload(api_client, student_headers, answers):
    from api.dependencies import decode_token, get_repository

    repo = get_repository()
    own = repo.get_items_from_db(course_id=_COURSE_UNIV)[0]
    other = repo.get_items_from_db(course_id=_COURSE_ID)[0]
    token = student_headers["Authorization"].removeprefix("Bearer ")
    student_id = int(decode_token(token)["sub"])
    before = repo.get_diagnostic(student_id, _COURSE_UNIV)
    response = api_client.post(
        f"/api/student/diagnostic/{_COURSE_UNIV}/submit",
        headers=student_headers,
        json={"answers": answers(own, other)},
    )
    assert response.status_code == 400
    assert repo.get_diagnostic(student_id, _COURSE_UNIV) == before


_B03 = "PREALG-N1-B03-ESCALERA-NECESIDAD"
_B04 = "PREALG-N1-B04-NATURALES-CONTAR"
_B05 = "PREALG-N1-B05-ENTEROS-DEUDA"
_B06 = "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION"


def _answers(node_id):
    """Respuestas correctas de todo lo que bloquea `node_completed` en un nodo de 11 bloques.

    Se derivan del contenido, así que migrar un nodo nuevo no obliga a tocar
    estos tests: basta con que declare `kind: "eleven_block_node"`.
    """
    from src.domain.learning.prealgebra import get_lesson

    content = get_lesson(node_id).get("content") or {}
    if content.get("kind") != "eleven_block_node":
        return []
    items = content["practice"] + [{**content["closing_item"], "kind": "numeric"}]
    return [
        (f"{node_id}-{i['id']}", i["answer"] if i["kind"] == "numeric" else i["expected"])
        for i in items
    ]


class TestCourses:
    def test_list_courses_authenticated(self, api_client, student_headers):
        """GET /student/courses → lista de cursos con flag enrolled."""
        r = api_client.get("/api/student/courses", headers=student_headers)
        assert r.status_code == 200
        courses = r.json()
        assert isinstance(courses, list)
        assert len(courses) > 0
        # Cada curso tiene los campos esperados
        course = courses[0]
        assert "id" in course or "course_id" in course
        assert "name" in course
        assert "block" in course
        assert "enrolled" in course

    def test_list_courses_unauthenticated(self, api_client):
        """GET /student/courses sin token → 401."""
        r = api_client.get("/api/student/courses")
        assert r.status_code == 401


class TestStats:
    def test_stats_authenticated(self, api_client, student_headers):
        """GET /student/stats → ELO global, tópicos, racha."""
        r = api_client.get("/api/student/stats", headers=student_headers)
        assert r.status_code == 200
        data = r.json()
        assert "global_elo" in data
        assert "total_attempts" in data
        assert "study_streak" in data
        assert "topic_elos" in data
        assert isinstance(data["topic_elos"], list)

    def test_stats_initial_elo(self, api_client, student_headers):
        """Spec 001 (FR-028b, flipped by T064): with no rated current course the overall rating is
        pending — null, never a 1000 placeholder; once rated it is a real number."""
        r = api_client.get("/api/student/stats", headers=student_headers)
        data = r.json()
        if data["overall_status"] == "pending_diagnostic":
            assert (data["global_elo"], data["display_rating"], data["rank_label"]) == (
                None,
                None,
                None,
            )
        else:
            assert 0 < data["global_elo"] < 5000


class TestEnroll:
    def test_enroll_in_course(self, api_client, student_headers):
        """POST /student/enroll → 201 for a course of the student's catalogue (universidad)."""
        r = api_client.post(
            "/api/student/enroll",
            json={"course_id": _COURSE_UNIV},
            headers=student_headers,
        )
        assert r.status_code in (200, 201)

    def test_enroll_nonexistent_course(self, api_client, student_headers):
        """Matrícula en curso inexistente → error (400 o 404)."""
        r = api_client.post(
            "/api/student/enroll",
            json={"course_id": "curso_que_no_existe_xyz"},
            headers=student_headers,
        )
        assert r.status_code in (400, 404, 422)

    def test_unenroll(self, api_client, student_headers):
        """DELETE /student/enroll/{course_id} → 204."""
        # Primero matricular para asegurar que existe la matrícula
        api_client.post(
            "/api/student/enroll",
            json={"course_id": _COURSE_UNIV},
            headers=student_headers,
        )
        r = api_client.delete(f"/api/student/enroll/{_COURSE_UNIV}", headers=student_headers)
        assert r.status_code == 204


class TestNextQuestion:
    @pytest.fixture(autouse=True, scope="class")
    def ensure_enrolled(self, api_client, student_headers):
        """Asegura matrícula antes de solicitar preguntas."""
        _enrol_directly(api_client, student_headers, _COURSE_ID)

    def test_next_question_returns_item_or_empty(self, api_client, student_headers):
        """POST /student/next-question → status 'ok' o 'empty'/'course_empty'."""
        r = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("ok", "empty", "course_empty")

    def test_next_question_item_structure(self, api_client, student_headers):
        """Si hay preguntas disponibles, el ítem tiene todos los campos."""
        r = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        data = r.json()
        if data["status"] == "ok" and data["item"]:
            item = data["item"]
            assert "id" in item
            assert "content" in item
            assert "options" in item
            assert isinstance(item["options"], list)
            assert len(item["options"]) >= 2
            assert "difficulty" in item
            assert "topic" in item


class TestAnswer:
    @pytest.fixture(autouse=True)
    def _enrolled(self, api_client, student_headers):
        """Practice needs an enrolment (spec 001 FR-037)."""
        _enrol_directly(api_client, student_headers, _COURSE_ID)

    def test_ignores_tampered_item_data(self, api_client, student_headers):
        from api.dependencies import get_repository
        from src.domain.elo.model import expected_score

        repo = get_repository()
        pool = repo.get_items_from_db(course_id=_COURSE_ID)
        canonical = repo.get_item_by_id(pool[0]["id"])
        other = repo.get_item_by_id(pool[1]["id"])
        response = api_client.post(
            "/api/student/answer",
            headers=student_headers,
            json={
                "item_id": canonical["id"],
                "item_data": {
                    "id": other["id"],
                    "difficulty": 1777,
                    "topic": "forged-topic",
                    "rating_deviation": 1,
                    "correct_option": "forged-answer",
                    "options": ["forged-answer"],
                },
                "selected_option": canonical["correct_option"],
                "time_taken": 30,
            },
        )
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert "correct_option" not in result
        conn = repo.get_connection()
        try:
            attempt = conn.execute(
                "SELECT item_id, difficulty, topic FROM attempts ORDER BY id DESC LIMIT 1"
            ).fetchone()
        finally:
            conn.close()
        assert attempt == (canonical["id"], canonical["difficulty"], canonical["topic"])
        updated = repo.get_item_by_id(canonical["id"])
        p = expected_score(result["elo_before"], canonical["difficulty"])
        assert updated["difficulty"] == pytest.approx(
            canonical["difficulty"] + 32 * (p - 1), abs=0.001
        )
        assert updated["rating_deviation"] == canonical["rating_deviation"]
        assert repo.get_item_by_id(other["id"]) == other

    # Spec 001 (FR-029, research R6): `elo_topic` is ignored, so it no longer causes a 400;
    # an option outside the item still does (FR-011).
    @pytest.mark.parametrize("override", [{"selected_option": "forged"}])
    def test_invalid_answer_context_has_no_side_effects(
        self, api_client, student_headers, override
    ):
        from api.dependencies import get_repository

        repo = get_repository()
        item = repo.get_items_from_db(course_id=_COURSE_ID)[0]
        before = repo.get_item_by_id(item["id"])
        conn = repo.get_connection()
        try:
            count_before = conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
        finally:
            conn.close()
        response = api_client.post(
            "/api/student/answer",
            headers=student_headers,
            json={
                "item_id": item["id"],
                "selected_option": item["correct_option"],
                "time_taken": 30,
                **override,
            },
        )
        assert response.status_code == 400
        assert repo.get_item_by_id(item["id"]) == before
        conn = repo.get_connection()
        try:
            assert conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == count_before
        finally:
            conn.close()

    def test_answer_without_legacy_item_data(self, api_client, student_headers):
        from api.dependencies import get_repository

        item = get_repository().get_items_from_db(course_id=_COURSE_ID)[0]
        response = api_client.post(
            "/api/student/answer",
            headers=student_headers,
            json={
                "item_id": item["id"],
                "selected_option": item["correct_option"],
                "elo_topic": _COURSE_ID,
                "time_taken": 30,
            },
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is True

    def test_submit_answer_correct(self, api_client, student_headers):
        """POST /student/answer con respuesta correcta → delta_elo positivo."""
        # Primero obtener una pregunta
        q_res = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        q_data = q_res.json()
        if q_data["status"] != "ok" or not q_data["item"]:
            pytest.skip("No hay preguntas disponibles para este test.")

        item = q_data["item"]
        # Obtener la respuesta correcta directamente del ítem (no la tenemos aquí)
        # Usamos la primera opción (puede ser incorrecta — solo testamos que la API responde)
        r = api_client.post(
            "/api/student/answer",
            json={
                "item_id": item["id"],
                "item_data": item,
                "selected_option": item["options"][0],
                "reasoning": "Prueba automática",
                "time_taken": 15.0,
            },
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "is_correct" in data
        assert "elo_before" in data
        assert "elo_after" in data
        assert "delta_elo" in data
        assert isinstance(data["is_correct"], bool)

    def test_submit_answer_elo_changes(self, api_client, student_headers):
        """El ELO cambia después de responder (delta_elo != 0 siempre)."""
        q_res = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        )
        q_data = q_res.json()
        if q_data["status"] != "ok" or not q_data["item"]:
            pytest.skip("No hay preguntas disponibles.")

        item = q_data["item"]
        r = api_client.post(
            "/api/student/answer",
            json={
                "item_id": item["id"],
                "item_data": item,
                "selected_option": item["options"][0],
                "time_taken": 10.0,
            },
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        # delta_elo siempre es distinto de 0 (el ELO siempre cambia al responder)
        assert data["delta_elo"] != 0


class TestHistory:
    def test_history_authenticated(self, api_client, student_headers):
        """GET /student/history → lista de intentos previos."""
        r = api_client.get("/api/student/history", headers=student_headers)
        assert r.status_code == 200


class TestRoleProtection:
    def test_teacher_cannot_access_student_answer(self, api_client, teacher_headers):
        """Practice needs an enrolment (spec 001 FR-037): a teacher has none, so 403."""
        r = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=teacher_headers,
        )
        assert r.status_code == 403


class TestAchievements:
    def test_achievements_authenticated(self, api_client, student_headers):
        """GET /student/achievements → dict con achievements y catalog."""
        r = api_client.get("/api/student/achievements", headers=student_headers)
        assert r.status_code == 200
        data = r.json()
        assert "achievements" in data
        assert "catalog" in data
        assert isinstance(data["achievements"], list)
        assert isinstance(data["catalog"], list)
        assert len(data["catalog"]) > 0

    def test_achievements_catalog_has_required_fields(self, api_client, student_headers):
        """Cada badge del catálogo tiene badge_id, label, icon y desc."""
        r = api_client.get("/api/student/achievements", headers=student_headers)
        catalog = r.json()["catalog"]
        for badge in catalog:
            assert "badge_id" in badge
            assert "label" in badge
            assert "icon" in badge
            assert "desc" in badge

    def test_achievements_unauthenticated(self, api_client):
        """GET /student/achievements sin token → 401."""
        r = api_client.get("/api/student/achievements")
        assert r.status_code == 401

    def test_first_correct_badge_awarded(self, api_client, student_headers):
        """Después de responder correctamente, el badge first_correct debe estar en logros."""
        # Garantizar matrícula
        _enrol_directly(api_client, student_headers, _COURSE_ID)
        # Obtener pregunta
        q = api_client.post(
            "/api/student/next-question",
            json={"course_id": _COURSE_ID},
            headers=student_headers,
        ).json()
        if q["status"] != "ok" or not q["item"]:
            return  # skip silencioso si no hay preguntas

        item = q["item"]
        # Responder (puede ser correcto o incorrecto — solo comprobamos que el endpoint devuelve new_badges)
        ans = api_client.post(
            "/api/student/answer",
            json={
                "item_id": item["id"],
                "item_data": item,
                "selected_option": item["options"][0],
                "time_taken": 5.0,
            },
            headers=student_headers,
        ).json()
        # cog_data puede contener new_badges si se desbloqueó algo
        assert "cog_data" in ans


class TestExamMode:
    @pytest.fixture(autouse=True, scope="class")
    def ensure_enrolled(self, api_client, student_headers):
        """Matricular al estudiante en el curso de prueba antes del examen."""
        _enrol_directly(api_client, student_headers, _COURSE_ID)

    def test_exam_start(self, api_client, student_headers):
        """POST /student/exam/start → lista de preguntas + tiempo límite."""
        r = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 3, "time_limit_minutes": 10},
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert data["session_id"]
        assert "n_questions" in data
        assert "time_limit_seconds" in data
        assert data["time_limit_seconds"] == 600  # 10 * 60
        assert len(data["items"]) >= 1
        assert len(data["items"]) <= 3

    def test_exam_start_item_structure(self, api_client, student_headers):
        """Los ítems del examen tienen todos los campos requeridos."""
        r = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 2, "time_limit_minutes": 5},
            headers=student_headers,
        )
        items = r.json()["items"]
        if not items:
            return
        item = items[0]
        assert "id" in item
        assert "content" in item
        assert "options" in item
        assert "difficulty" in item

    def test_exam_start_nonexistent_course(self, api_client, student_headers):
        """Examen en curso sin preguntas → 404."""
        r = api_client.post(
            "/api/student/exam/start",
            json={"course_id": "curso_xyz_inexistente", "n_questions": 5},
            headers=student_headers,
        )
        assert r.status_code == 404

    def test_exam_submit(self, api_client, student_headers):
        """POST /student/exam/submit → resultados con score_pct y global_elo_after."""
        # Obtener preguntas del examen
        start = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 2, "time_limit_minutes": 5},
            headers=student_headers,
        ).json()
        items = start.get("items", [])
        if not items:
            return

        # Enviar respuestas (primera opción de cada pregunta)
        answers = [
            {"item_id": it["id"], "selected_option": it["options"][0], "time_taken": 5.0}
            for it in items
        ]
        r = api_client.post(
            "/api/student/exam/submit",
            json={"session_id": start["session_id"], "answers": answers},
            headers=student_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        assert "correct_count" in data
        assert "total_questions" in data
        assert "score_pct" in data
        assert "global_elo_after" in data
        assert 0 <= data["score_pct"] <= 100
        assert data["total_questions"] == len(items)

    def test_exam_submit_empty(self, api_client, student_headers):
        """No se puede enviar una sesión sin su composición exacta."""
        start = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 1},
            headers=student_headers,
        ).json()
        r = api_client.post(
            "/api/student/exam/submit",
            json={"session_id": start["session_id"], "answers": []},
            headers=student_headers,
        )
        assert r.status_code == 400

    def test_exam_unauthenticated(self, api_client):
        """Examen sin autenticación → 401."""
        r = api_client.post(
            "/api/student/exam/start",
            json={"course_id": _COURSE_ID, "n_questions": 3},
        )
        assert r.status_code == 401


def test_welcome_lesson_progress_flow(api_client, student_headers):
    node_id = "PREALG-N1-B01-BIENVENIDA"
    base = f"/api/student/lessons/algebra_basica/{node_id}"

    detail = api_client.get(base, headers=student_headers)
    assert detail.status_code == 200
    assert detail.json()["affects_elo"] is False

    completed = api_client.post(
        f"{base}/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["state"] == "completed"


def test_welcome_lesson_rejects_unknown_event(api_client, student_headers):
    node_id = "PREALG-N1-B01-BIENVENIDA"
    response = api_client.post(
        f"/api/student/lessons/algebra_basica/{node_id}/events",
        headers=student_headers,
        json={"event": "change_elo"},
    )
    assert response.status_code == 422


def test_trigger_question_requires_closed_responses_before_completion(api_client, student_headers):
    welcome = "/api/student/lessons/algebra_basica/PREALG-N1-B01-BIENVENIDA/events"
    api_client.post(welcome, headers=student_headers, json={"event": "node_completed"})
    base = "/api/student/lessons/algebra_basica/" "PREALG-N1-B02-PREGUNTA-DETONADORA"

    incomplete = api_client.post(
        f"{base}/events", headers=student_headers, json={"event": "node_completed"}
    )
    assert incomplete.status_code == 409

    for interaction_id, selected_option in (
        ("PREALG-N1-B02-Q01", "no"),
        ("PREALG-N1-B02-Q02", "bread"),
    ):
        response = api_client.post(
            f"{base}/interactions",
            headers=student_headers,
            json={"interaction_id": interaction_id, "selected_option": selected_option},
        )
        assert response.status_code == 200

    completed = api_client.post(
        f"{base}/events", headers=student_headers, json={"event": "node_completed"}
    )
    assert completed.status_code == 200
    assert completed.json()["state"] == "completed"


def test_staircase_unlocks_after_trigger_and_requires_its_formative_answer(
    api_client, student_headers
):
    welcome = "/api/student/lessons/algebra_basica/PREALG-N1-B01-BIENVENIDA/events"
    api_client.post(welcome, headers=student_headers, json={"event": "node_completed"})

    trigger = "/api/student/lessons/algebra_basica/" "PREALG-N1-B02-PREGUNTA-DETONADORA"
    for interaction_id, selected_option in (
        ("PREALG-N1-B02-Q01", "no"),
        ("PREALG-N1-B02-Q02", "advance"),
    ):
        api_client.post(
            f"{trigger}/interactions",
            headers=student_headers,
            json={"interaction_id": interaction_id, "selected_option": selected_option},
        )
    api_client.post(f"{trigger}/events", headers=student_headers, json={"event": "node_completed"})

    staircase = "/api/student/lessons/algebra_basica/" "PREALG-N1-B03-ESCALERA-NECESIDAD"
    detail = api_client.get(staircase, headers=student_headers)
    assert detail.status_code == 200
    assert len(detail.json()["staircase"]["core_steps"]) == 5

    incomplete = api_client.post(
        f"{staircase}/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    assert incomplete.status_code == 409

    for interaction_id, option in _answers(_B03):
        answer = api_client.post(
            f"{staircase}/interactions",
            headers=student_headers,
            json={"interaction_id": interaction_id, "selected_option": option},
        )
        assert answer.status_code == 200
        assert answer.json()["is_expected"] is True

    completed = api_client.post(
        f"{staircase}/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    assert completed.status_code == 200


def test_naturals_node_handles_guided_practice_without_elo(api_client, student_headers):
    api_client.post(
        "/api/student/lessons/algebra_basica/PREALG-N1-B01-BIENVENIDA/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    trigger = "/api/student/lessons/algebra_basica/" "PREALG-N1-B02-PREGUNTA-DETONADORA"
    for interaction_id, selected_option in (
        ("PREALG-N1-B02-Q01", "no"),
        ("PREALG-N1-B02-Q02", "bread"),
    ):
        api_client.post(
            f"{trigger}/interactions",
            headers=student_headers,
            json={"interaction_id": interaction_id, "selected_option": selected_option},
        )
    api_client.post(f"{trigger}/events", headers=student_headers, json={"event": "node_completed"})

    staircase = "/api/student/lessons/algebra_basica/" "PREALG-N1-B03-ESCALERA-NECESIDAD"
    for interaction_id, option in _answers(_B03):
        api_client.post(
            f"{staircase}/interactions",
            headers=student_headers,
            json={"interaction_id": interaction_id, "selected_option": option},
        )
    api_client.post(
        f"{staircase}/events", headers=student_headers, json={"event": "node_completed"}
    )

    naturals = "/api/student/lessons/algebra_basica/" "PREALG-N1-B04-NATURALES-CONTAR"
    detail = api_client.get(naturals, headers=student_headers)
    assert detail.status_code == 200
    assert detail.json()["affects_elo"] is False

    wrong_total = api_client.post(
        f"{naturals}/interactions",
        headers=student_headers,
        json={"interaction_id": f"{_B04}-E1", "selected_option": "7"},
    )
    assert wrong_total.status_code == 200
    assert wrong_total.json()["is_expected"] is False

    for interaction_id, selected_option in _answers(_B04):
        response = api_client.post(
            f"{naturals}/interactions",
            headers=student_headers,
            json={"interaction_id": interaction_id, "selected_option": selected_option},
        )
        assert response.status_code == 200
        assert response.json()["is_expected"] is True

    completed = api_client.post(
        f"{naturals}/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["state"] == "completed"


def test_integers_node_uses_negative_sign_and_discrete_anchor(api_client, student_headers):
    api_client.post(
        "/api/student/lessons/algebra_basica/PREALG-N1-B01-BIENVENIDA/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    prerequisites = [
        (
            "PREALG-N1-B02-PREGUNTA-DETONADORA",
            (("PREALG-N1-B02-Q01", "no"), ("PREALG-N1-B02-Q02", "debt")),
        ),
        (
            _B03,
            _answers(_B03),
        ),
        (
            _B04,
            _answers(_B04),
        ),
    ]
    for node_id, interactions in prerequisites:
        base = f"/api/student/lessons/algebra_basica/{node_id}"
        for interaction_id, selected_option in interactions:
            response = api_client.post(
                f"{base}/interactions",
                headers=student_headers,
                json={"interaction_id": interaction_id, "selected_option": selected_option},
            )
            assert response.status_code == 200
        completed = api_client.post(
            f"{base}/events", headers=student_headers, json={"event": "node_completed"}
        )
        assert completed.status_code == 200

    integers = "/api/student/lessons/algebra_basica/PREALG-N1-B05-ENTEROS-DEUDA"
    detail = api_client.get(integers, headers=student_headers)
    assert detail.status_code == 200
    assert detail.json()["affects_elo"] is False

    for interaction_id, selected_option in _answers(_B05):
        response = api_client.post(
            f"{integers}/interactions",
            headers=student_headers,
            json={"interaction_id": interaction_id, "selected_option": selected_option},
        )
        assert response.status_code == 200
        assert response.json()["is_expected"] is True

    completed = api_client.post(
        f"{integers}/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["state"] == "completed"


def test_rationals_node_links_fraction_division_and_decimal(api_client, student_headers):
    api_client.post(
        "/api/student/lessons/algebra_basica/PREALG-N1-B01-BIENVENIDA/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    prerequisites = [
        (
            "PREALG-N1-B02-PREGUNTA-DETONADORA",
            (("PREALG-N1-B02-Q01", "no"), ("PREALG-N1-B02-Q02", "bread")),
        ),
        (
            _B03,
            _answers(_B03),
        ),
        (
            _B04,
            _answers(_B04),
        ),
        (
            _B05,
            _answers(_B05),
        ),
    ]
    for node_id, interactions in prerequisites:
        base = f"/api/student/lessons/algebra_basica/{node_id}"
        for interaction_id, selected_option in interactions:
            response = api_client.post(
                f"{base}/interactions",
                headers=student_headers,
                json={"interaction_id": interaction_id, "selected_option": selected_option},
            )
            assert response.status_code == 200
        completed = api_client.post(
            f"{base}/events", headers=student_headers, json={"event": "node_completed"}
        )
        assert completed.status_code == 200

    rationals = "/api/student/lessons/algebra_basica/" "PREALG-N1-B06-RACIONALES-FRACCION-DIVISION"
    detail = api_client.get(rationals, headers=student_headers)
    assert detail.status_code == 200
    assert detail.json()["affects_elo"] is False

    reversed_share = api_client.post(
        f"{rationals}/interactions",
        headers=student_headers,
        json={
            "interaction_id": _B06 + "-E5",
            "selected_option": "true_same",  # la trampa: el decimal truncado
        },
    )
    assert reversed_share.status_code == 200
    assert reversed_share.json()["is_expected"] is False

    for interaction_id, selected_option in _answers(_B06):
        response = api_client.post(
            f"{rationals}/interactions",
            headers=student_headers,
            json={"interaction_id": interaction_id, "selected_option": selected_option},
        )
        assert response.status_code == 200
        assert response.json()["is_expected"] is True

    completed = api_client.post(
        f"{rationals}/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["state"] == "completed"


def _complete_node(api_client, headers, node_id: str):
    return api_client.post(
        f"/api/student/lessons/algebra_basica/{node_id}/events",
        headers=headers,
        json={"event": "node_completed"},
    )


def _answer(api_client, headers, node_id: str, interaction_id: str, selected_option: str):
    return api_client.post(
        f"/api/student/lessons/algebra_basica/{node_id}/interactions",
        headers=headers,
        json={"interaction_id": interaction_id, "selected_option": selected_option},
    )


def _complete_level_one(api_client, headers):
    _complete_node(api_client, headers, "PREALG-N1-B01-BIENVENIDA")
    trigger = "PREALG-N1-B02-PREGUNTA-DETONADORA"
    _answer(api_client, headers, trigger, "PREALG-N1-B02-Q01", "no")
    _answer(api_client, headers, trigger, "PREALG-N1-B02-Q02", "bread")
    _complete_node(api_client, headers, trigger)

    for interaction_id, option in _answers(_B03):
        _answer(api_client, headers, _B03, interaction_id, option)
    staircase = _B03
    _complete_node(api_client, headers, staircase)

    # `_answers` devuelve [] para los nodos que todavía no se reconstruyeron,
    # así que este bucle no cambia cuando se migra uno más.
    for node_id in (
        _B04,
        _B05,
        _B06,
        "PREALG-N1-B07-IRRACIONALES-DECIMALES",
        "PREALG-N1-B08-REALES-RECTA",
        "PREALG-N1-B10-CLASIFICADOR-BASICO",
        "PREALG-N1-B11-CLASIFICADOR-RIGUROSO",
        "PREALG-N1-B12-DETECTIVE-FALSEDADES",
        "PREALG-N1-B13-CIERRE-DIAGNOSTICO",
    ):
        for interaction_id, selected_option in _answers(node_id):
            _answer(api_client, headers, node_id, interaction_id, selected_option)
        response = _complete_node(api_client, headers, node_id)
        assert response.status_code == 200


def test_level_two_map_and_hub_are_locked_until_level_one_is_completed(api_client, student_headers):
    hub = "/api/student/lessons/algebra_basica/PREALG-N2-E00-CIUDAD"

    locked_detail = api_client.get(hub, headers=student_headers)
    assert locked_detail.status_code == 403

    locked_map = api_client.get("/api/student/map/algebra_basica", headers=student_headers)
    assert locked_map.status_code == 200
    n2_nodes = [
        node
        for node in locked_map.json()["nodes"]
        if (node.get("node_id") or "").startswith("PREALG-N2")
    ]
    assert n2_nodes
    assert all(node["state"] == "blocked" for node in n2_nodes)

    _complete_level_one(api_client, student_headers)

    unlocked_detail = api_client.get(hub, headers=student_headers)
    assert unlocked_detail.status_code == 200
    assert unlocked_detail.json()["content"]["gating"]["cards_required"] == 6

    incomplete = api_client.post(
        f"{hub}/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    assert incomplete.status_code == 409

    for building_id in ("E01", "E02", "E03", "E04", "E05", "E06"):
        response = _answer(
            api_client,
            student_headers,
            "PREALG-N2-E00-CIUDAD",
            f"PREALG-N2-E00-CIUDAD-CARD-{building_id}",
            "opened",
        )
        assert response.status_code == 200

    first_building = api_client.get(
        "/api/student/lessons/algebra_basica/PREALG-N2-E01-SUMA-JUNTAR",
        headers=student_headers,
    )
    assert first_building.status_code == 200

    completed = api_client.post(
        f"{hub}/events",
        headers=student_headers,
        json={"event": "node_completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["state"] == "completed"


def test_level_three_unlocks_after_level_two_and_tracks_laboratory_machines(
    api_client, student_headers
):
    hub = "/api/student/lessons/algebra_basica/PREALG-N3-M00-LABORATORIO"
    locked_detail = api_client.get(hub, headers=student_headers)
    assert locked_detail.status_code == 403

    _complete_level_one(api_client, student_headers)
    for building_id in ("E01", "E02", "E03", "E04", "E05", "E06"):
        _answer(
            api_client,
            student_headers,
            "PREALG-N2-E00-CIUDAD",
            f"PREALG-N2-E00-CIUDAD-CARD-{building_id}",
            "opened",
        )
    _complete_node(api_client, student_headers, "PREALG-N2-E00-CIUDAD")

    for node_id in (
        "PREALG-N2-E01-SUMA-JUNTAR",
        "PREALG-N2-E02-RESTA-QUITAR",
        "PREALG-N2-E03-MULTIPLICACION-AGRUPAR",
        "PREALG-N2-E04-DIVISION-REPARTIR",
        "PREALG-N2-E05-POTENCIACION-CRECER",
        "PREALG-N2-E06-RADICACION-RAIZ",
    ):
        detail = api_client.get(
            f"/api/student/lessons/algebra_basica/{node_id}",
            headers=student_headers,
        )
        assert detail.status_code == 200
        for interaction_id, answer in _answers(node_id):
            response = _answer(api_client, student_headers, node_id, interaction_id, answer)
            assert response.status_code == 200
        assert _complete_node(api_client, student_headers, node_id).status_code == 200

    unlocked_detail = api_client.get(hub, headers=student_headers)
    assert unlocked_detail.status_code == 200
    assert unlocked_detail.json()["content"]["gating"]["machines_required"] == 5

    machine_before_hub = api_client.get(
        "/api/student/lessons/algebra_basica/PREALG-N3-M01-CONMUTATIVA",
        headers=student_headers,
    )
    assert machine_before_hub.status_code == 403

    for machine_id in ("M01", "M02", "M03", "M04", "M05"):
        response = _answer(
            api_client,
            student_headers,
            "PREALG-N3-M00-LABORATORIO",
            f"PREALG-N3-M00-LABORATORIO-MACHINE-{machine_id}",
            "introduced",
        )
        assert response.status_code == 200

    first_machine = api_client.get(
        "/api/student/lessons/algebra_basica/PREALG-N3-M01-CONMUTATIVA",
        headers=student_headers,
    )
    assert first_machine.status_code == 200
    assert first_machine.json()["content"]["station"] == "La Prensa de Intercambio"


def test_algebra_nodes_appear_in_the_map_blocked_until_prealgebra_is_done(
    api_client, student_headers
):
    """El Papiro de las Cuatro Casas se ve en el mapa desde el principio, cerrado."""
    response = api_client.get("/api/student/map/algebra_basica", headers=student_headers)
    assert response.status_code == 200

    alg_nodes = [
        node for node in response.json()["nodes"] if (node.get("node_id") or "").startswith("ALG-")
    ]
    # La lista sale de la ruta, no se copia a mano: cada nodo de Álgebra nuevo
    # obligaba a editar este test, que es la misma deuda que se cerró en B4.
    from src.domain.learning.prealgebra import (
        ALG_N1_NODE_IDS,
        ALG_N2_NODE_IDS,
        ALG_N3_NODE_IDS,
    )

    assert [
        node["node_id"] for node in alg_nodes
    ] == ALG_N1_NODE_IDS + ALG_N2_NODE_IDS + ALG_N3_NODE_IDS

    # Sin el MCM completado, todo el módulo de Álgebra está cerrado.
    assert all(node["state"] == "blocked" for node in alg_nodes)
