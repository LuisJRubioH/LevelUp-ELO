"""
tests/integration/test_sqlite_repository.py
============================================
Pruebas de integración con SQLite en archivo temporal.
Verifican el ciclo completo sin tocar la DB de desarrollo.

El fixture `repo` usa tmp_path de pytest → la DB se elimina al terminar el test.
"""

import json
import pytest
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository


@pytest.fixture
def repo(tmp_path) -> SQLiteRepository:
    """Repositorio con DB en archivo temporal — se elimina al terminar el test."""
    db_path = str(tmp_path / "test_levelup.db")
    return SQLiteRepository(db_name=db_path)


class TestBankLoading:
    def test_bank_loading_with_utf8_characters(self, tmp_path, repo):
        """Ítems con caracteres UTF-8 (ñ, tildes, LaTeX) se cargan sin error."""
        bank_file = tmp_path / "test_course.json"
        items = [
            {
                "id": "utf8_test_01",
                "content": "Ecuación cuadrática con coeficientes reáles: $ax^2 + bx + c = 0$",
                "difficulty": 800,
                "topic": "Álgebra",
                "options": [
                    "$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$",
                    "$x = b$",
                ],
                "correct_option": "$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$",
            }
        ]
        bank_file.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")

        # Verificar lectura UTF-8
        with open(bank_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded[0]["id"] == "utf8_test_01"
        assert "reáles" in loaded[0]["content"]
        assert "Álgebra" in loaded[0]["topic"]

    def test_repo_initializes_without_error(self, repo):
        """El repositorio se inicializa correctamente en archivo temporal."""
        assert repo is not None
        assert repo.db_name is not None


class TestAtomicTransaction:
    def test_save_answer_transaction_persists_attempt(self, repo):
        """save_answer_transaction persiste el intento en la tabla attempts."""
        # Registrar un usuario y obtener su ID
        ok, msg = repo.register_user(
            "test_student",
            "password123",
            "student",
            education_level="universidad",
        )
        assert ok, f"No se pudo registrar el usuario: {msg}"

        user = repo.login_user("test_student", "password123")
        assert user is not None
        user_id = user[0]

        # Obtener un ítem del banco real (si existe)
        conn = repo.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, difficulty FROM items LIMIT 1")
            row = cur.fetchone()
        finally:
            conn.close()

        if row is None:
            pytest.skip("No hay ítems en el banco de test — se necesita al menos 1")

        item_id, item_difficulty = row[0], row[1]

        # Ejecutar transacción atómica
        attempt_data = {
            "is_correct": True,
            "difficulty": item_difficulty,
            "topic": "Test",
            "elo_after": 1050.0,
            "prob_failure": 0.4,
            "expected_score": 0.6,
            "time_taken": 10.0,
            "confidence_score": None,
            "error_type": "none",
            "rating_deviation": 300.0,
        }
        repo.save_answer_transaction(
            user_id=user_id,
            item_id=item_id,
            item_difficulty_new=item_difficulty + 5,
            item_rd_new=200.0,
            attempt_data=attempt_data,
        )

        # Verificar que el intento quedó guardado
        conn2 = repo.get_connection()
        try:
            cur2 = conn2.cursor()
            cur2.execute(
                "SELECT COUNT(*) FROM attempts WHERE user_id = ? AND item_id = ?",
                (user_id, item_id),
            )
            count = cur2.fetchone()[0]
        finally:
            conn2.close()

        assert count == 1

    def test_register_and_login_roundtrip(self, repo):
        """Registro + login devuelven el mismo usuario."""
        ok, _ = repo.register_user(
            "rondtrip_user",
            "pass1234",
            "student",
            education_level="colegio",
        )
        assert ok

        user = repo.login_user("rondtrip_user", "pass1234")
        assert user is not None
        _, username, role, _ = user
        assert username == "rondtrip_user"
        assert role == "student"
