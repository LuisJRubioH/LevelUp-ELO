"""
Reporte mensual del motor ELO — LevelUp-ELO.

Ejecutar el primer dia de cada mes:
    python scripts/monthly_metrics.py

Siempre filtra: elo_valid=1, is_test_user=0.
"""

import sys
import os
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.metrics import roc_auc_score, log_loss


def cargar_repo():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        return PostgresRepository()
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

    return SQLiteRepository()


def metricas_nivel(datos, nivel_label):
    y_true = np.array([d["is_correct"] for d in datos], dtype=float)
    y_pred = np.array([d["expected_score"] for d in datos], dtype=float)
    mask = ~np.isnan(y_pred)
    y_true, y_pred = y_true[mask], y_pred[mask]
    if len(y_true) < 30:
        return None
    return {
        "n": len(y_true),
        "auc": roc_auc_score(y_true, y_pred),
        "sesgo": float((y_pred - y_true).mean()),
        "logloss": log_loss(y_true, y_pred),
    }


def reporte(repo):
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"REPORTE MENSUAL — LevelUp-ELO — {datetime.now().strftime('%Y-%m-%d')}")
    print(sep)

    todos = repo.get_all_attempts_for_calibration(exclude_test_users=True)

    if not todos:
        print("Sin datos validos — ejecutar tras registrar intentos reales.")
        return

    # Global
    m = metricas_nivel(todos, "global")
    if m:
        print(f"\nN intentos (elo_valid=1, is_test_user=0): {m['n']}")
        print(f"AUC global : {m['auc']:.4f}  (meta: >=0.70)")
        flag_auc = "OK" if m["auc"] >= 0.70 else "BAJO"
        print(f"Sesgo      : {m['sesgo']:+.4f}  (meta: <0.05)  [{flag_auc}]")
        print(f"Log-loss   : {m['logloss']:.4f}")

    # Por nivel
    niveles = ["semillero", "colegio", "universidad"]
    print("\n--- Por nivel ---")
    for nivel in niveles:
        sub = [d for d in todos if d.get("education_level") == nivel]
        m_nivel = metricas_nivel(sub, nivel)
        if m_nivel:
            flag = "OK" if m_nivel["auc"] >= 0.70 else "BAJO"
            print(
                f"  {nivel:<15} n={m_nivel['n']:<5} "
                f"AUC={m_nivel['auc']:.4f} [{flag}]  "
                f"sesgo={m_nivel['sesgo']:+.4f}"
            )
        else:
            print(f"  {nivel:<15} sin datos suficientes (<30 intentos validos)")

    # Items problematicos
    item_stats = defaultdict(lambda: {"n": 0, "ok": 0, "p_preds": []})
    for d in todos:
        s = item_stats[d["item_id"]]
        s["n"] += 1
        s["ok"] += d["is_correct"]
        if d.get("expected_score") is not None:
            s["p_preds"].append(d["expected_score"])

    problematicos = [(iid, s) for iid, s in item_stats.items() if s["n"] >= 10 and s["ok"] == 0]

    print(f"\n--- Items con 0% exito (>=10 intentos): {len(problematicos)} ---")
    if problematicos:
        for iid, s in sorted(problematicos, key=lambda x: -x[1]["n"]):
            p_pred = np.mean(s["p_preds"]) if s["p_preds"] else float("nan")
            print(f"  {iid:<30} n={s['n']:<5} P_pred_media={p_pred:.3f}")
        print("  -> Recalibrar o retirar antes de la proxima sesion.")
    else:
        print("  Ninguno.")

    # Estado calibrador
    from src.domain.elo.calibration import IsotonicCalibrator

    cal = IsotonicCalibrator()
    activo = cal.load()
    print(f"\n--- Calibrador isotónico ---")
    print(f"  Estado: {'ACTIVO' if activo else 'NO ENTRENADO'}")
    if not activo:
        print("  Ejecutar: python scripts/train_calibrator.py")

    print(f"\n{sep}\n")


if __name__ == "__main__":
    repo = cargar_repo()
    reporte(repo)
