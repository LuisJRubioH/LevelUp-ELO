"""Arma el banco de preguntas de Evaluar para Avanzar 8 desde los fragmentos fuente.

`items/source/epa8/*.json` es el dataset de trabajo: trae todo lo que necesitan los
tres consumidores (ejemplos resueltos, ejercicios propuestos y banco) — enunciado
limpio, opciones, respuesta, pasos de solución, misconception por distractor,
taxonomía ICFES y la referencia a la figura reconstruida.

Este script proyecta esos fragmentos al formato del banco
(`items/bank/evaluar_para_avanzar_8.json`) y valida lo que valida el motor.

    python scripts/build_epa8_bank.py
    python scripts/build_epa8_bank.py --check   # no escribe: verifica los fuentes y que el
                                                # banco sea, byte a byte, lo que este script
                                                # escribe (spec 008 FR-012, D6)

El banco de EPA8 no se edita a mano: se edita el fuente y se regenera.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.domain.bank.rules import difficulty_problem  # noqa: E402  (spec 008 FR-010)

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


def proyectar(item: dict) -> dict:
    """El ítem en el formato del banco. El tema del fuente («Pensamiento aleatorio — porcentaje
    sobre un total») se parte: lo de antes de « — » es el `topic`, que lleva el rating, y el resto
    el `subtopic`, solo para estudio (spec 008 FR-040, FR-041)."""
    destino = {}
    for campo in CAMPOS_BANCO:
        if campo not in item:
            continue
        if campo == "topic":
            tema, _, subtema = item["topic"].partition(" — ")
            destino["topic"] = tema
            if subtema:
                destino["subtopic"] = subtema
        else:
            destino[campo] = item[campo]
    return destino


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
        problema = difficulty_problem(item["difficulty"])
        if problema:
            problemas.append(f"{ident}: {problema}")
        for ruta in [item.get("image_url")] + list(item.get("options_images") or []):
            if ruta and not (ROOT / ruta).exists():
                problemas.append(f"{ident}: falta la figura {ruta} (corre scripts/figuras_epa8.py)")
    return problemas


def render(items: list[dict]) -> str:
    """El texto exacto del banco: la proyección, con `image_url` (lo consume el ingestor)."""
    banco = [proyectar(item) for item in items]
    for destino, origen in zip(banco, items):
        if origen.get("image_url"):
            destino["image_url"] = origen["image_url"]
    return json.dumps(banco, ensure_ascii=False, indent=2) + "\n"


def diferencias(esperado: str, actual: str) -> str:
    """Qué difiere entre el banco que se escribiría y el que hay, en palabras."""
    try:
        nuevos = {i.get("id"): i for i in json.loads(esperado)}
        viejos = {i.get("id"): i for i in json.loads(actual)}
    except (json.JSONDecodeError, AttributeError, TypeError):
        return "el archivo no es la lista JSON que escribe el generador"
    ids = sorted(i for i in set(nuevos) | set(viejos) if nuevos.get(i) != viejos.get(i))
    if not ids:
        return "mismos ítems, distinto formato (espacios, orden o escapes)"
    return "ítems distintos: " + ", ".join(map(str, ids[:10])) + (" …" if len(ids) > 10 else "")


def comparar(items: list[dict], banco: Path) -> int:
    """Spec 008 FR-012 (D6, O-V9): el banco es, byte a byte, la salida del generador."""
    esperado = render(items)
    if not banco.is_file():
        motivo = "el archivo no existe"
    else:
        actual = banco.read_text(encoding="utf-8")
        if actual == esperado:
            print(f"{banco.name} es la salida del generador")
            return 0
        motivo = diferencias(esperado, actual)
    print(f"ERROR  {banco.name} no es la salida del generador: {motivo}")
    print(
        f"       regenera con `python scripts/build_epa8_bank.py` desde "
        f"{FUENTE.relative_to(ROOT)}/; no edites el banco a mano (spec 008 FR-012)"
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="solo validar, no escribir")
    parser.add_argument(
        "--bank",
        type=Path,
        default=BANCO,
        help="banco a comparar con --check (por defecto el real)",
    )
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
        return comparar(items, args.bank)

    BANCO.write_text(render(items), encoding="utf-8")
    print(f"Escrito {BANCO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
