"""
tests/unit/domain/test_entities.py
====================================
Pruebas de los dataclasses de dominio:
- Student: validación de nivel educativo, propiedades block y level_label
- ProcedureSubmission: validación de status, propiedades is_pending_validation / is_validated
"""
import pytest
from src.domain.entities import (
    Student,
    ProcedureSubmission,
    LEVEL_UNIVERSIDAD,
    LEVEL_COLEGIO,
    LEVEL_CONCURSOS,
    LEVEL_SEMILLERO,
    PROC_STATUS_PENDING,
    PROC_STATUS_PENDING_VALIDATION,
    PROC_STATUS_VALIDATED,
)


class TestStudent:
    def test_valid_universidad_level(self):
        """Nivel 'universidad' → creación exitosa."""
        s = Student(id=1, username="ana", level="universidad")
        assert s.level == LEVEL_UNIVERSIDAD

    def test_valid_colegio_level(self):
        """Nivel 'colegio' → creación exitosa."""
        s = Student(id=2, username="pedro", level="colegio")
        assert s.level == LEVEL_COLEGIO

    def test_level_is_normalized_to_lowercase(self):
        """El nivel se normaliza a minúsculas en __post_init__."""
        s = Student(id=3, username="maria", level="Universidad")
        assert s.level == "universidad"

    def test_invalid_level_raises_value_error(self):
        """Nivel no válido → ValueError."""
        with pytest.raises(ValueError, match="inválido"):
            Student(id=4, username="bad", level="primaria")

    def test_block_property_for_universidad(self):
        """Propiedad block retorna 'Universidad' para nivel universidad."""
        s = Student(id=1, username="u1", level="universidad")
        assert s.block == "Universidad"

    def test_block_property_for_colegio(self):
        """Propiedad block retorna 'Colegio' para nivel colegio."""
        s = Student(id=2, username="u2", level="colegio")
        assert s.block == "Colegio"

    def test_level_label_property_returns_string(self):
        """level_label retorna un string no vacío para todos los niveles válidos."""
        for lvl in [LEVEL_UNIVERSIDAD, LEVEL_COLEGIO, LEVEL_CONCURSOS, LEVEL_SEMILLERO]:
            s = Student(id=1, username="x", level=lvl)
            label = s.level_label
            assert isinstance(label, str)
            assert len(label) > 0


class TestProcedureSubmission:
    def test_valid_pending_status(self):
        """Status 'pending' → creación exitosa."""
        sub = ProcedureSubmission(
            id=1, student_id=10, item_id="item_01", status=PROC_STATUS_PENDING
        )
        assert sub.status == PROC_STATUS_PENDING

    def test_valid_pending_validation_status(self):
        """Status PENDING_TEACHER_VALIDATION → creación exitosa."""
        sub = ProcedureSubmission(
            id=2, student_id=10, item_id="item_01",
            status=PROC_STATUS_PENDING_VALIDATION
        )
        assert sub.is_pending_validation is True
        assert sub.is_validated is False

    def test_valid_validated_status(self):
        """Status VALIDATED_BY_TEACHER → is_validated=True."""
        sub = ProcedureSubmission(
            id=3, student_id=10, item_id="item_01", status=PROC_STATUS_VALIDATED
        )
        assert sub.is_validated is True
        assert sub.is_pending_validation is False

    def test_invalid_status_raises_value_error(self):
        """Status no reconocido → ValueError."""
        with pytest.raises(ValueError, match="inválido"):
            ProcedureSubmission(
                id=4, student_id=10, item_id="item_01", status="desconocido"
            )

    def test_optional_fields_default_to_none(self):
        """ai_proposed_score, teacher_score y final_score son opcionales."""
        sub = ProcedureSubmission(
            id=5, student_id=10, item_id="item_01", status=PROC_STATUS_PENDING
        )
        assert sub.ai_proposed_score is None
        assert sub.teacher_score is None
        assert sub.final_score is None
