"""
Entrena y guarda el calibrador isotónico sobre datos de producción.

Uso:
    python scripts/train_calibrator.py
    python scripts/train_calibrator.py --level semillero
    python scripts/train_calibrator.py --level colegio
    python scripts/train_calibrator.py --level universidad

Requiere que ML-1 (elo_valid) esté implementado.
Siempre filtra is_test_user=0 (luisito-s y torieg excluidos).
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.metrics import roc_auc_score, log_loss

from src.domain.elo.calibration import IsotonicCalibrator

MIN_INTENTOS = 50
MIN_INTENTOS_RECOMENDADO = 500


def cargar_datos(level: str = None):
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        from src.infrastructure.persistence.postgres_repository import PostgresRepository

        repo = PostgresRepository()
    else:
        from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

        repo = SQLiteRepository()

    return repo.get_all_attempts_for_calibration(
        education_level=level,
        exclude_test_users=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Entrenar calibrador isotónico")
    parser.add_argument(
        "--level",
        default="global",
        choices=["global", "semillero", "colegio", "universidad"],
        help="Nivel educativo a calibrar (default: global)",
    )
    args = parser.parse_args()

    nivel = args.level
    education_level = None if nivel == "global" else nivel

    print(f"\n=== Calibrador isotónico — nivel: {nivel} ===")

    datos = cargar_datos(education_level)
    n = len(datos)

    if n < MIN_INTENTOS:
        print(f"ERROR: solo {n} intentos validos — minimo requerido: {MIN_INTENTOS}")
        print("       Esperar mas datos antes de calibrar.")
        sys.exit(1)

    if n < MIN_INTENTOS_RECOMENDADO:
        print(
            f"AVISO: {n} intentos — calibracion poco confiable (recomendado: {MIN_INTENTOS_RECOMENDADO}+)"
        )

    y_true = np.array([d["is_correct"] for d in datos], dtype=float)
    y_pred = np.array([d["expected_score"] for d in datos], dtype=float)

    # Filtrar filas con expected_score nulo (intentos antiguos sin ese campo)
    mask = ~np.isnan(y_pred)
    y_true, y_pred = y_true[mask], y_pred[mask]
    n_validos = int(mask.sum())

    if n_validos < MIN_INTENTOS:
        print(f"ERROR: solo {n_validos} intentos con expected_score — minimo: {MIN_INTENTOS}")
        sys.exit(1)

    print(f"Intentos cargados: {n} total, {n_validos} con expected_score")

    # Metricas antes
    auc_antes = roc_auc_score(y_true, y_pred)
    sesgo_antes = float((y_pred - y_true).mean())
    ll_antes = log_loss(y_true, y_pred)
    print(f"\nANTES  — AUC: {auc_antes:.4f} | Sesgo: {sesgo_antes:+.4f} | Log-loss: {ll_antes:.4f}")

    # Entrenar y guardar
    os.makedirs("models", exist_ok=True)
    path = f"models/isotonic_calibrator_{nivel}.pkl"
    calibrador = IsotonicCalibrator()
    metricas = calibrador.train_and_save(y_true, y_pred, path=path)

    print(
        f"DESPUES — AUC: {metricas['auc_after']:.4f} | "
        f"Sesgo: {metricas['bias_after']:+.4f} | "
        f"Log-loss: {metricas['logloss_after']:.4f}"
    )
    print(f"\nMejora sesgo: {abs(sesgo_antes):.4f} -> {abs(metricas['bias_after']):.4f}")

    if abs(metricas["bias_after"]) > 0.05:
        print("AVISO: sesgo sigue > 0.05 tras calibracion — revisar datos de entrada")

    delta_auc = metricas["auc_after"] - auc_antes
    if abs(delta_auc) > 0.002:
        print(f"AVISO: AUC cambio {delta_auc:+.4f} — isotonic no deberia cambiar AUC")

    print(f"\nCalibrador guardado en: {path}")

    # Copiar tambien como calibrador por defecto si es global
    if nivel == "global":
        import shutil

        shutil.copy(path, IsotonicCalibrator.MODEL_PATH)
        print(f"Copiado como calibrador por defecto: {IsotonicCalibrator.MODEL_PATH}")


if __name__ == "__main__":
    main()
