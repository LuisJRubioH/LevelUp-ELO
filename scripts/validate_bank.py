"""
scripts/validate_bank.py
========================
Valida la estructura e integridad de todos los ítems del banco de preguntas.

Uso:
    python scripts/validate_bank.py

Retorna exit code 0 si todo está OK.
Retorna exit code 1 si hay errores (útil para CI/CD y pre-commit hooks).

Qué verifica:
    - Encoding UTF-8 válido en todos los archivos
    - Sintaxis JSON válida
    - Campos requeridos presentes en cada ítem
    - correct_option existe en options (coincidencia exacta)
    - Dificultad en rango válido [100, 3000]
    - Mínimo 2 opciones por ítem
    - IDs únicos en todo el banco (sin duplicados entre archivos)
"""

import json
import sys
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────────
BANK_DIR = Path("items/bank")
REQUIRED_FIELDS = {"id", "content", "difficulty", "topic", "options", "correct_option"}
DIFFICULTY_RANGE = (100, 3000)
MIN_OPTIONS = 2

# ── Estado global del validador ────────────────────────────────────────────────
errors: list = []
warnings: list = []


def validate_item(item: dict, source_file: str) -> None:
    """Valida un ítem individual. Agrega a errors/warnings según corresponda."""
    item_id = item.get("id", "<sin id>")
    prefix = f"[{source_file}] Item '{item_id}'"

    # 1. Campos requeridos
    missing = REQUIRED_FIELDS - set(item.keys())
    if missing:
        errors.append(f"{prefix}: faltan campos requeridos: {sorted(missing)}")
        return  # Sin campos base, no tiene sentido seguir validando

    # 2. correct_option debe estar en options (comparación exacta, carácter por carácter)
    if item["correct_option"] not in item["options"]:
        errors.append(
            f"{prefix}: correct_option='{item['correct_option']}' "
            f"NO está en options. Options disponibles: {item['options']}"
        )

    # 3. Dificultad en rango
    try:
        d = float(item["difficulty"])
    except (TypeError, ValueError):
        errors.append(f"{prefix}: difficulty='{item['difficulty']}' no es un número")
        d = -1

    if d != -1 and not (DIFFICULTY_RANGE[0] <= d <= DIFFICULTY_RANGE[1]):
        warnings.append(
            f"{prefix}: difficulty={d} fuera del rango recomendado "
            f"[{DIFFICULTY_RANGE[0]}, {DIFFICULTY_RANGE[1]}]"
        )

    # 4. Mínimo de opciones
    if not isinstance(item["options"], list):
        errors.append(f"{prefix}: 'options' debe ser una lista, es {type(item['options'])}")
    elif len(item["options"]) < MIN_OPTIONS:
        errors.append(
            f"{prefix}: tiene {len(item['options'])} opción(es), "
            f"mínimo requerido: {MIN_OPTIONS}"
        )

    # 5. ID no vacío
    if not str(item.get("id", "")).strip():
        errors.append(f"{prefix}: 'id' está vacío o es solo espacios")

    # 6. Content no vacío
    if not str(item.get("content", "")).strip():
        errors.append(f"{prefix}: 'content' está vacío")


def validate_file(json_file: Path) -> list:
    """
    Carga y valida un archivo JSON del banco.
    Retorna la lista de ítems si es válido, lista vacía si hay error de carga.
    """
    # Verificar encoding UTF-8
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except UnicodeDecodeError as e:
        errors.append(
            f"[{json_file.name}]: Error de encoding UTF-8: {e}. "
            f"Guardar el archivo como UTF-8 sin BOM."
        )
        return []

    # Verificar JSON válido
    try:
        items = json.loads(raw_content)
    except json.JSONDecodeError as e:
        errors.append(f"[{json_file.name}]: JSON inválido en línea {e.lineno}: {e.msg}")
        return []

    # Debe ser una lista
    if not isinstance(items, list):
        errors.append(
            f"[{json_file.name}]: el contenido debe ser un array JSON (lista), "
            f"pero es {type(items).__name__}"
        )
        return []

    # Lista vacía es warning, no error
    if len(items) == 0:
        warnings.append(f"[{json_file.name}]: el archivo está vacío (0 ítems)")
        return []

    return items


def main() -> None:
    # Verificar que el banco existe
    if not BANK_DIR.exists():
        print(f"ERROR: No se encontró el directorio '{BANK_DIR}'.")
        print("Ejecuta este script desde la raíz del proyecto.")
        sys.exit(1)

    json_files = sorted(BANK_DIR.rglob("*.json"))
    if not json_files:
        print(f"ERROR: No se encontraron archivos .json en '{BANK_DIR}'")
        sys.exit(1)

    # ── Procesar todos los archivos ─────────────────────────────────────────
    all_items = []  # (item_id, source_file)
    total_items = 0

    for json_file in json_files:
        items = validate_file(json_file)
        for item in items:
            validate_item(item, json_file.name)
            if "id" in item:
                all_items.append((str(item["id"]), json_file.name))
        total_items += len(items)

    # ── Verificar IDs duplicados globales ────────────────────────────────────
    seen_ids = {}
    for item_id, source_file in all_items:
        if item_id in seen_ids:
            errors.append(
                f"ID DUPLICADO '{item_id}': aparece en '{source_file}' "
                f"y en '{seen_ids[item_id]}'"
            )
        else:
            seen_ids[item_id] = source_file

    # ── Reporte final ────────────────────────────────────────────────────────
    print(f"\n{'='*65}")
    print(f"  Banco de preguntas — Reporte de validación")
    print(f"{'='*65}")
    print(f"  Archivos analizados : {len(json_files)}")
    print(f"  Ítems encontrados   : {total_items}")
    print(f"  IDs únicos          : {len(seen_ids)}")
    print(f"{'='*65}")

    if warnings:
        print(f"\n  ADVERTENCIAS ({len(warnings)}):")
        for w in warnings:
            print(f"   • {w}")

    if errors:
        print(f"\n  ERRORES ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")
        print(f"\n  Validación FALLIDA. Corregir los errores antes de continuar.")
        print(f"  Los ítems con errores no se cargarán correctamente en producción.\n")
        sys.exit(1)
    else:
        print(f"\n  Validación EXITOSA. El banco está íntegro y listo.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
