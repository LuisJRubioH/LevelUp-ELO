"""
Calibrador isotónico para las predicciones del motor ELO.

Corrige el sesgo sistemático (+0.165 global) sin modificar el ranking
relativo ni el cálculo de deltas ELO. Solo afecta expected_score guardado
en attempts (lo que ven los dashboards).

Referencia: Zadrozny & Elkan (2002). Transforming classifier scores into
accurate multiclass probability estimates. KDD 2002.
"""

import os
import pickle


class IsotonicCalibrator:
    """
    Envuelve sklearn IsotonicRegression para uso en producción.

    Regla crítica: el calibrador corrige expected_score GUARDADO en attempts.
    El motor ELO SIEMPRE calcula deltas con expected_score RAW.
    Nunca pasar el valor calibrado al cálculo del delta ELO.

    Uso:
        calibrator = IsotonicCalibrator()
        calibrator.load()                      # False si no existe → sin excepción
        p_display = calibrator.predict(p_raw)  # para guardar en DB
        delta = K * (actual - p_raw)           # siempre raw para ELO
    """

    MODEL_PATH = "models/isotonic_calibrator.pkl"

    def __init__(self):
        self._model = None
        self._trained = False

    def load(self, path: str = None) -> bool:
        """Carga el calibrador entrenado. Retorna False silenciosamente si no existe."""
        path = path or self.MODEL_PATH
        if not os.path.exists(path):
            return False
        try:
            with open(path, "rb") as f:
                self._model = pickle.load(f)
            self._trained = True
            return True
        except Exception:
            return False

    def predict(self, p_raw: float) -> float:
        """Aplica calibración. Retorna p_raw si no hay modelo. Nunca lanza excepción."""
        if not self._trained or self._model is None:
            return p_raw
        try:
            import numpy as np

            p = float(self._model.predict(np.array([[p_raw]]))[0])
            return max(0.001, min(0.999, p))
        except Exception:
            return p_raw

    def train_and_save(self, y_true, y_pred, path: str = None) -> dict:
        """Entrena sobre datos y guarda el modelo. Retorna métricas antes/después."""
        import numpy as np
        from sklearn.isotonic import IsotonicRegression
        from sklearn.metrics import roc_auc_score, log_loss

        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)

        auc_before = roc_auc_score(y_true, y_pred)
        bias_before = float((y_pred - y_true).mean())
        ll_before = log_loss(y_true, y_pred)

        ir = IsotonicRegression(out_of_bounds="clip")
        ir.fit(y_pred.reshape(-1, 1), y_true)
        y_cal = ir.predict(y_pred.reshape(-1, 1))

        auc_after = roc_auc_score(y_true, y_cal)
        bias_after = float((y_cal - y_true).mean())
        ll_after = log_loss(y_true, y_cal)

        save_path = path or self.MODEL_PATH
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        with open(save_path, "wb") as f:
            pickle.dump(ir, f)
        self._model = ir
        self._trained = True

        return {
            "auc_before": auc_before,
            "auc_after": auc_after,
            "bias_before": bias_before,
            "bias_after": bias_after,
            "logloss_before": ll_before,
            "logloss_after": ll_after,
            "n": len(y_true),
        }

    @property
    def is_active(self) -> bool:
        return self._trained
