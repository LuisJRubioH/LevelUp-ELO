"""
tests/api/test_pvp.py
======================
Tests de los endpoints REST nuevos:
  GET /api/student/blocks/{course_id}  → bloques temáticos de concursos
  GET /api/student/pvp/history         → historial de partidas PvP

El flujo WebSocket completo de la partida se verifica aparte (lógica en
tests/unit/infrastructure/test_pvp_logic.py); aquí solo los endpoints HTTP.
"""

import pytest


class TestCourseBlocks:
    def test_dian_blocks_returned(self, api_client, student_headers):
        """DIAN tiene bloques temáticos con conteo de ítems."""
        r = api_client.get("/api/student/blocks/DIAN", headers=student_headers)
        assert r.status_code == 200
        blocks = r.json()
        assert isinstance(blocks, list)
        assert len(blocks) > 0
        b = blocks[0]
        assert "block" in b
        assert "item_count" in b
        assert b["item_count"] > 0

    def test_blocks_require_auth(self, api_client):
        r = api_client.get("/api/student/blocks/DIAN")
        assert r.status_code == 401

    def test_unknown_course_returns_empty(self, api_client, student_headers):
        r = api_client.get("/api/student/blocks/__no_existe__", headers=student_headers)
        assert r.status_code == 200
        assert r.json() == []

    def test_math_course_has_no_blocks(self, api_client, student_headers):
        """Un curso de matemáticas (sin campo block) devuelve lista vacía."""
        r = api_client.get("/api/student/blocks/calculo_diferencial", headers=student_headers)
        assert r.status_code == 200
        assert r.json() == []


class TestPvpHistory:
    def test_history_returns_list(self, api_client, student_headers):
        """El historial PvP responde 200 con una página: una lista (vacía si no hay partidas) y si
        hay más (spec 007 FR-060)."""
        r = api_client.get("/api/student/pvp/history", headers=student_headers)
        assert r.status_code == 200
        assert isinstance(r.json()["matches"], list)
        assert isinstance(r.json()["has_more"], bool)

    def test_history_requires_auth(self, api_client):
        r = api_client.get("/api/student/pvp/history")
        assert r.status_code == 401

    @pytest.mark.parametrize("before", [0, -1, 2_147_483_648, 10**20])
    def test_a_cursor_outside_the_match_ids_is_refused(self, api_client, student_headers, before):
        """Spec 007 FR-060: `before` is a match id (PostgreSQL INTEGER). Outside 1 … 2³¹−1 it
        is refused with 422 instead of reaching the query (PostgreSQL: integer out of range)."""
        r = api_client.get(f"/api/student/pvp/history?before={before}", headers=student_headers)
        assert r.status_code == 422


class TestLeagueStats:
    """Spec 007 FR-070 (delivery S): the League's answers for study, beside the practice ones."""

    def test_the_students_league_stats_have_their_shape(self, api_client, student_headers):
        r = api_client.get("/api/student/league/stats", headers=student_headers)
        assert r.status_code == 200
        body = r.json()
        assert set(body) == {"answers", "correct", "topics", "items"}
        assert isinstance(body["topics"], list) and isinstance(body["items"], list)

    def test_the_students_league_stats_require_auth(self, api_client):
        assert api_client.get("/api/student/league/stats").status_code == 401

    def test_the_teachers_view_requires_auth(self, api_client):
        assert api_client.get("/api/teacher/student/1/league").status_code == 401

    def test_the_teachers_view_is_for_teachers(self, api_client, student_headers):
        r = api_client.get("/api/teacher/student/1/league", headers=student_headers)
        assert r.status_code == 403

    def test_a_student_outside_the_teachers_set_is_not_found(self, api_client, teacher_headers):
        r = api_client.get("/api/teacher/student/987654/league", headers=teacher_headers)
        assert r.status_code == 404
