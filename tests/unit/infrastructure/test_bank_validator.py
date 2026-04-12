"""
tests/unit/infrastructure/test_bank_validator.py
=================================================
Pruebas del validador de banco de preguntas (scripts/validate_bank.py).

El validador usa listas globales `errors` y `warnings` que se reinician
en cada test vía setup_method para evitar contaminación entre pruebas.
"""
import json
import sys
import pytest
from pathlib import Path

# Agregar scripts/ al path para importar validate_bank
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))


class TestValidateItem:
    """Pruebas de la función validate_item() del validador."""

    def setup_method(self):
        """Limpiar estado global del validador antes de cada test."""
        import validate_bank
        validate_bank.errors.clear()
        validate_bank.warnings.clear()
        self.validate_item = validate_bank.validate_item
        self.errors = validate_bank.errors
        self.warnings = validate_bank.warnings

    def test_valid_item_produces_no_errors(self):
        """Ítem bien formado → sin errores."""
        item = {
            "id": "q1",
            "content": "¿Cuánto es 2+2?",
            "difficulty": 800,
            "topic": "Aritmética",
            "options": ["3", "4", "5", "6"],
            "correct_option": "4",
        }
        self.validate_item(item, "test.json")
        assert len(self.errors) == 0

    def test_correct_option_not_in_options_is_error(self):
        """correct_option que no está en options → error."""
        item = {
            "id": "q2",
            "content": "Pregunta",
            "difficulty": 800,
            "topic": "Álgebra",
            "options": ["A", "B", "C"],
            "correct_option": "D",
        }
        self.validate_item(item, "test.json")
        assert any("q2" in e for e in self.errors)
        assert any("correct_option" in e for e in self.errors)

    def test_missing_required_field_is_error(self):
        """Falta el campo difficulty → error."""
        item = {
            "id": "q3",
            "content": "Pregunta sin difficulty",
            "topic": "Álgebra",
            "options": ["A", "B"],
            "correct_option": "A",
        }
        self.validate_item(item, "test.json")
        assert len(self.errors) > 0
        assert any("difficulty" in e.lower() or "faltan" in e.lower()
                   for e in self.errors)

    def test_single_option_is_error(self):
        """Solo 1 opción → error (mínimo 2 opciones)."""
        item = {
            "id": "q4",
            "content": "Pregunta",
            "difficulty": 800,
            "topic": "Álgebra",
            "options": ["Solo una"],
            "correct_option": "Solo una",
        }
        self.validate_item(item, "test.json")
        assert any("opci" in e.lower() or "option" in e.lower()
                   for e in self.errors)

    def test_out_of_range_difficulty_is_warning_not_error(self):
        """Dificultad fuera de [100, 3000] → advertencia, no error crítico."""
        item = {
            "id": "q5",
            "content": "Pregunta",
            "difficulty": 5000,
            "topic": "Álgebra",
            "options": ["A", "B"],
            "correct_option": "A",
        }
        self.validate_item(item, "test.json")
        assert len(self.errors) == 0
        assert len(self.warnings) > 0

    def test_non_numeric_difficulty_is_error(self):
        """difficulty no numérica → error."""
        item = {
            "id": "q6",
            "content": "Pregunta",
            "difficulty": "alta",
            "topic": "Álgebra",
            "options": ["A", "B"],
            "correct_option": "A",
        }
        self.validate_item(item, "test.json")
        assert len(self.errors) > 0

    def test_multiple_valid_options_no_error(self):
        """Ítem con 4 opciones válidas → sin errores."""
        item = {
            "id": "q7",
            "content": "Elige la correcta",
            "difficulty": 1000,
            "topic": "Lógica",
            "options": ["A", "B", "C", "D"],
            "correct_option": "C",
        }
        self.validate_item(item, "test.json")
        assert len(self.errors) == 0


class TestValidateFile:
    """Pruebas de la función validate_file() del validador."""

    def setup_method(self):
        import validate_bank
        validate_bank.errors.clear()
        validate_bank.warnings.clear()
        self.validate_file = validate_bank.validate_file
        self.errors = validate_bank.errors

    def test_valid_utf8_json_loads_correctly(self, tmp_path):
        """JSON UTF-8 con caracteres especiales → carga sin errores."""
        json_file = tmp_path / "valid.json"
        items = [
            {
                "id": "q1",
                "content": "Contenido con ñ y tildes: ó é á",
                "difficulty": 800,
                "topic": "Test",
                "options": ["Sí", "No"],
                "correct_option": "Sí",
            }
        ]
        json_file.write_text(json.dumps(items), encoding="utf-8")
        result = self.validate_file(json_file)
        assert len(result) == 1
        assert len(self.errors) == 0

    def test_invalid_encoding_produces_error(self, tmp_path):
        """Archivo con encoding inválido (no UTF-8) → error, retorna lista vacía."""
        json_file = tmp_path / "bad_encoding.json"
        json_file.write_bytes(b'[{"id": "bad", "content": "\x8d\x9d"}]')
        result = self.validate_file(json_file)
        assert result == []
        assert any(
            "encoding" in e.lower() or "unicode" in e.lower()
            for e in self.errors
        )

    def test_invalid_json_produces_error(self, tmp_path):
        """JSON con sintaxis inválida → error, retorna lista vacía."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text('[{"id": "bad" INVALID}]', encoding="utf-8")
        result = self.validate_file(json_file)
        assert result == []
        assert any(
            "json" in e.lower() or "inválido" in e.lower() or "invalid" in e.lower()
            for e in self.errors
        )

    def test_empty_array_returns_empty_list(self, tmp_path):
        """JSON con array vacío → retorna lista vacía, sin errores de parse."""
        json_file = tmp_path / "empty.json"
        json_file.write_text("[]", encoding="utf-8")
        result = self.validate_file(json_file)
        assert result == []
        assert len(self.errors) == 0
