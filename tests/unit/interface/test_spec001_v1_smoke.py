"""
V1 smoke pin (spec 001, task T021; constitution § Stack: V1 is frozen, never left broken).

Imports every V1 view and builds the services exactly as `src/interface/streamlit/app.py`
does, without a Streamlit runtime. Stays green at every spec 001 checkpoint: a task that
changes a shared signature adapts its V1 call sites in the same task.
"""

import importlib

import pytest

pytest.importorskip("streamlit", reason="V1 stack (requirements.txt) not installed")


@pytest.mark.parametrize("view", ["auth_view", "admin_view", "teacher_view", "student_view"])
def test_spec001_v1_view_imports(view):
    importlib.import_module(f"src.interface.streamlit.views.{view}")


def test_spec001_v1_services_compose_as_app_py(tmp_path):
    import src.application.services.student_service as ss_mod
    import src.application.services.teacher_service as ts_mod
    from src.infrastructure.external_api.ai_client import get_pedagogical_analysis
    from src.infrastructure.ml.calibration import IsotonicCalibrator
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    db = SQLiteRepository(db_name=str(tmp_path / "v1_smoke.db"))
    calibrator = IsotonicCalibrator()
    calibrator.load()

    student = ss_mod.StudentService(db, calibrator=calibrator)
    teacher = ts_mod.TeacherService(db, pedagogical_analysis=get_pedagogical_analysis)

    assert student.repository is db
    assert teacher is not None
