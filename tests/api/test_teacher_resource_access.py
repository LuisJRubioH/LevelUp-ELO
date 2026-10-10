"""Permisos por recurso docente contra SQLite temporal, sin proveedores externos."""

from contextlib import closing
from unittest.mock import Mock
import uuid

import pytest


@pytest.fixture
def resources(api_client, teacher_token):
    from api.dependencies import create_access_token, decode_token, get_repository

    repo = get_repository()
    teacher_id = int(decode_token(teacher_token)["sub"])
    group_id = repo.get_groups_by_teacher(teacher_id)[0]["group_id"]
    suffix = uuid.uuid4().hex
    with closing(repo.get_connection()) as conn:
        other_id = conn.execute(
            "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, ?, 1)",
            (f"access_teacher_{suffix}", "unused", "teacher"),
        ).lastrowid
        student_id = conn.execute(
            "INSERT INTO users (username, password_hash, role, group_id) VALUES (?, ?, ?, ?)",
            (f"access_student_{suffix}", "unused", "student", group_id),
        ).lastrowid
        ungrouped_id = conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (f"ungrouped_{suffix}", "unused", "student"),
        ).lastrowid
        conn.commit()
    token = create_access_token(other_id, f"access_teacher_{suffix}", "teacher")
    return {
        "repo": repo,
        "teacher_id": teacher_id,
        "group_id": group_id,
        "student_id": student_id,
        "ungrouped_id": ungrouped_id,
        "other_id": other_id,
        "other_headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.mark.parametrize(
    "suffix", ["", "/elo-history", "/katia-history", "/ranking", "/ai-analysis"]
)
def test_student_routes_require_current_teacher_relationship(
    api_client, teacher_headers, resources, monkeypatch, suffix
):
    from api.config import settings
    from src.application.services.teacher_service import TeacherService

    # The analysis is mocked; a key only gets past the "no key configured" answer.
    monkeypatch.setattr(settings, "system_ai_api_key", "gsk_test_only")
    analysis = Mock(return_value="Análisis local")
    monkeypatch.setattr(TeacherService, "generate_ai_analysis", analysis)
    method = "POST" if suffix == "/ai-analysis" else "GET"
    base = "/api/teacher/student/"
    for student_id, headers in [
        (resources["student_id"], resources["other_headers"]),
        (resources["ungrouped_id"], teacher_headers),
        (resources["teacher_id"], teacher_headers),
        (99999999, teacher_headers),
    ]:
        response = api_client.request(method, f"{base}{student_id}{suffix}", headers=headers)
        assert response.status_code == 404
    analysis.assert_not_called()
    own = api_client.request(
        method, f"{base}{resources['student_id']}{suffix}", headers=teacher_headers
    )
    assert own.status_code == 200
    if suffix == "/ai-analysis":
        analysis.assert_called_once()

    # La autorización se reevalúa después de una reasignación de grupo.
    with closing(resources["repo"].get_connection()) as conn:
        conn.execute("UPDATE users SET group_id=NULL WHERE id=?", (resources["student_id"],))
        conn.commit()
    assert (
        api_client.request(
            method, f"{base}{resources['student_id']}{suffix}", headers=teacher_headers
        ).status_code
        == 404
    )


def test_foreign_invite_code_is_not_rotated(api_client, teacher_headers, resources):
    repo = resources["repo"]
    group_id = resources["group_id"]
    before = repo.generate_group_invite_code(group_id)
    for target in (group_id, 99999999):
        response = api_client.post(
            f"/api/teacher/groups/{target}/invite-code", headers=resources["other_headers"]
        )
        assert response.status_code == 404
    assert repo.get_group_by_invite_code(before)["group_id"] == group_id
    own = api_client.post(f"/api/teacher/groups/{group_id}/invite-code", headers=teacher_headers)
    assert own.status_code == 200
    assert own.json()["invite_code"]


def test_assignment_must_belong_to_authorized_template(api_client, teacher_headers, resources):
    repo = resources["repo"]
    item = repo.get_items_from_db(course_id="calculo_diferencial")[0]
    own = repo.create_exam_template(
        resources["teacher_id"], "calculo_diferencial", "Own", 10, [item["id"]]
    )
    foreign = repo.create_exam_template(
        resources["other_id"], "calculo_diferencial", "Foreign", 10, [item["id"]]
    )
    assignment = repo.create_exam_assignment(foreign, resources["group_id"], None, None)
    before = repo.list_assignments_for_template(foreign)
    base = "/api/teacher/exam-templates"
    for template_id, assignment_id, expected in [
        (own, assignment, 404),
        (own, 99999999, 404),
        (foreign, assignment, 403),
    ]:
        response = api_client.delete(
            f"{base}/{template_id}/assignments/{assignment_id}", headers=teacher_headers
        )
        assert response.status_code == expected
        assert repo.list_assignments_for_template(foreign) == before
    legitimate = repo.create_exam_assignment(own, resources["group_id"], None, None)
    assert (
        api_client.delete(
            f"{base}/{own}/assignments/{legitimate}", headers=teacher_headers
        ).status_code
        == 204
    )
    assert repo.list_assignments_for_template(own) == []
    assert repo.list_assignments_for_template(foreign) == before


def test_ai_analysis_without_a_key_says_so(api_client, teacher_headers, resources, monkeypatch):
    """No key anywhere → 422 naming the setting, as KatIA and the procedure review answer."""
    from api.config import settings

    for attr in ("system_ai_api_key", "ai_key_teacher_analysis"):
        monkeypatch.setattr(settings, attr, "")
    response = api_client.post(
        f"/api/teacher/student/{resources['student_id']}/ai-analysis", headers=teacher_headers
    )
    assert response.status_code == 422
    assert "SYSTEM_AI_API_KEY" in response.json()["detail"]


@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
def test_ai_analysis_with_an_unreachable_model_answers_503(
    api_client, teacher_headers, resources, monkeypatch, error
):
    """ai_client raises these with a user-facing message; they used to surface as a 500."""
    from api.config import settings
    from src.application.services.teacher_service import TeacherService

    monkeypatch.setattr(settings, "system_ai_api_key", "gsk_test_only")
    message = "⚠️ No se pudo conectar al modelo. Intenta de nuevo en unos segundos."
    monkeypatch.setattr(TeacherService, "generate_ai_analysis", Mock(side_effect=error(message)))
    response = api_client.post(
        f"/api/teacher/student/{resources['student_id']}/ai-analysis", headers=teacher_headers
    )
    assert response.status_code == 503
    assert response.json()["detail"] == message
