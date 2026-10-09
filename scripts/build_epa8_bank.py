"""Arma el banco de preguntas de Evaluar para Avanzar 8 desde los fragmentos fuente.

`items/source/epa8/*.json` es el dataset de trabajo: trae todo lo que necesitan los
tres consumidores (ejemplos resueltos, ejercicios propuestos y banco) — enunciado
limpio, opciones, respuesta, pasos de solución, misconception por distractor,
taxonomía ICFES y la referencia a la figura reconstruida.

Este script proyecta esos fragmentos al formato del banco
(`items/bank/evaluar_para_avanzar_8.json`) y valida lo que valida el motor.

    python scripts/build_epa8_bank.py
    python scripts/build_epa8_bank.py --check   # no escribe, solo verifica
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUENTE = ROOT / "items" / "source" / "epa8"
BANCO = ROOT / "items" / "bank" / "evaluar_para_avanzar_8.json"
ASSETS = ROOT / "items" / "assets" / "epa8"

# Campos que viajan al banco. El resto (solution, misconception_by_option,
# pensamiento, source, figura...) se queda en el fuente: el ingestor los ignora
# y no tiene sentido cargarlos en la DB en cada arranque.
CAMPOS_BANCO = ("id", "content", "difficulty", "topic", "options", "correct_option", "tags")


def cargar() -> list[dict]:
    items: list[dict] = []
    for archivo in sorted(FUENTE.glob("*.json")):
        items.extend(json.loads(archivo.read_text(encoding="utf-8")))
    return items


def revisar(items: list[dict]) -> list[str]:
    problemas: list[str] = []
    vistos: set[str] = set()
    for item in items:
        ident = item.get("id", "<sin id>")
        if ident in vistos:
            problemas.append(f"{ident}: id duplicado")
        vistos.add(ident)
        if item["correct_option"] not in item["options"]:
            problemas.append(f"{ident}: correct_option no coincide con ninguna opción")
        if len(item["options"]) < 2:
            problemas.append(f"{ident}: menos de 2 opciones")
        if not 100 <= item["difficulty"] <= 3000:
            problemas.append(f"{ident}: dificultad fuera de [100, 3000]")
        for ruta in [item.get("image_url")] + list(item.get("options_images") or []):
            if ruta and not (ROOT / ruta).exists():
                problemas.append(f"{ident}: falta la figura {ruta} (corre scripts/figuras_epa8.py)")
    return problemas


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="solo validar, no escribir")
    args = parser.parse_args()

    items = cargar()
    if not items:
        print(f"Sin fragmentos en {FUENTE.relative_to(ROOT)}")
        return 1

    problemas = revisar(items)
    for p in problemas:
        print(f"ERROR  {p}")
    if problemas:
        return 1

    con_figura = sum(1 for i in items if i.get("image_url") or i.get("options_images"))
    print(f"{len(items)} ítems OK · {con_figura} con figura reconstruida")

    if args.check:
        return 0

    banco = [{k: item[k] for k in CAMPOS_BANCO if k in item} for item in items]
    # image_url sí lo consume el ingestor; se conserva cuando existe.
    for destino, origen in zip(banco, items):
        if origen.get("image_url"):
            destino["image_url"] = origen["image_url"]
    BANCO.write_text(json.dumps(banco, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Escrito {BANCO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
