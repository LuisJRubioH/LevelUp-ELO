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
        """El historial PvP responde 200 con una lista (vacía si no hay partidas)."""
        r = api_client.get("/api/student/pvp/history", headers=student_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_history_requires_auth(self, api_client):
        r = api_client.get("/api/student/pvp/history")
        assert r.status_code == 401
