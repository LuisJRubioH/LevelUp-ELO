"""
Survey 008 B15 (`docs/sdd/item-bank-survey.md` § 7): the student API built an IsotonicCalibrator
and read its model from disk on every request (`_make_service`). It is loaded once per process
and shared; with no trained model it still returns the raw probability (display only — the
rating always uses the raw value).
"""

from api.routers import student
from src.infrastructure.ml.calibration import IsotonicCalibrator


def test_the_calibrator_is_loaded_once_per_process(monkeypatch):
    loads = []
    real_load = IsotonicCalibrator.load

    def counting_load(self, path=None):
        loads.append(path)
        return real_load(self, path)

    monkeypatch.setattr(IsotonicCalibrator, "load", counting_load)
    student._calibrator.cache_clear()

    first, second = student._make_service(object()), student._make_service(object())

    assert len(loads) == 1
    assert first._calibrator is second._calibrator
    student._calibrator.cache_clear()


def test_without_a_model_the_shared_calibrator_returns_the_raw_value(monkeypatch):
    monkeypatch.setattr(IsotonicCalibrator, "MODEL_PATH", "models/__does_not_exist__.pkl")
    student._calibrator.cache_clear()

    assert student._make_service(object())._calibrator.predict(0.37) == 0.37
    student._calibrator.cache_clear()
