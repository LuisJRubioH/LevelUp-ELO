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
    - Dificultad: un entero JSON en 400–2000, como error (spec 008 FR-010, D1)
    - Mínimo 2 opciones por ítem
    - IDs únicos en todo el banco (sin duplicados entre archivos)
    - Ningún texto entre dos `$` que no sea matemática (dos montos en pesos en la misma frase
      convierten lo de en medio en una fórmula)
    - Ningún carácter de control (R5): `"\\frac"` escrito con una sola barra en el JSON se lee
      como salto de página + "rac"
    - `topic` es texto no vacío; `subtopic`, si está, también (spec 008 FR-040)
    - Un tema con menos de 5 ítems en su curso da un aviso, no un error (FR-043)
    - `id` es texto no vacío; `tags`, si está, es una lista de textos no vacíos
    - La imagen (`image_url` o `image_path`), si está, existe en el repositorio
    - Cada archivo es un curso del catálogo de cursos (`src/domain/bank/catalogue.py`) con
      bloque y nombre explícito; un archivo de `semillero/` se llama
      `<materia>_semillero_<g>` (g de 6 a 11) y no necesita entrada; una entrada del catálogo sin
      archivo es un error (spec 008 FR-020, FR-021)
    - Ningún id cambia de curso ni de tema frente a `items/id_manifest.json`; un id nuevo entra
      con `python scripts/update_id_manifest.py`; un id del manifiesto no desaparece del banco;
      sin manifiesto, error (spec 008 FR-011, D4)
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # run as `python scripts/validate_bank.py`, from any directory

from src.domain.bank import catalogue, rules  # noqa: E402  (stdlib only: the CI job installs none)

# ── Configuración ──────────────────────────────────────────────────────────────
BANK_DIR = Path("items/bank")
REQUIRED_FIELDS = {"id", "content", "difficulty", "topic", "options", "correct_option"}
MANIFEST = Path(rules.MANIFEST_PATH)
MIN_OPTIONS = 2
SMALL_TOPIC = 5  # spec 008 FR-043: a topic with fewer items warns

# The frontend's MathText split (frontend/src/components/Math/MathContent.tsx): what it renders as
# math. V1's st.markdown also reads $…$ as math.
_MATH_TOKEN = re.compile(
    r"(\$\$(?:\\\$|[\s\S])*?\$\$|\\\[[\s\S]+?\\\]"
    r"|(?<!\\)\$(?:\\\$|[^$\n])+?(?<!\\)\$|\\\([\s\S]+?\\\))"
)
_WORD = re.compile(r"(?<![\\\w])[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{3,}")


def prose_read_as_math(text: str) -> list:
    """Spans rendered as a formula that are really prose: two or more words, no TeX at all.

    "un capital de $10 millones importa maquinaria por $5.000 millones" turns
    "10 millones importa maquinaria por " into one italic formula with its spaces dropped.
    """
    found = []
    for token in _MATH_TOKEN.findall(text):
        body = token.strip("$")
        if "\\" not in body and "{" not in body and len(_WORD.findall(body)) >= 2:
            found.append(token)
    return found


_DOLLAR = re.compile(r"(?<!\\)\$")


def control_characters(text: str) -> list:
    """R5: what a LaTeX command written with ONE backslash in the JSON decodes to.

    `\\f`, `\\b`, `\\t`, `\\r` («\\frac», «\\beta», «\\theta», «\\right») become control
    characters, which the bank never needs. A newline is Markdown (lists, tables), so it is an
    error only when it cuts a formula in two («$a \\neq b$»): the line before it then holds an odd
    number of `$`.
    """
    found = [repr(ch) for ch in text if ch != "\n" and (ord(ch) < 32 or 127 <= ord(ch) < 160)]
    lines = text.split("\n")
    if len(lines) > 1:
        found += [
            "'\\n' dentro de una fórmula"
            for line in lines
            if len(_DOLLAR.findall(line.replace("$$", ""))) % 2
        ][:1]
    return found


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

    # 3. Dificultad: un entero JSON en 400–2000 (spec 008 FR-010)
    problem = rules.difficulty_problem(item["difficulty"])
    if problem:
        errors.append(f"{prefix}: {problem}")

    # 4. Mínimo de opciones
    if not isinstance(item["options"], list):
        errors.append(f"{prefix}: 'options' debe ser una lista, es {type(item['options'])}")
    elif len(item["options"]) < MIN_OPTIONS:
        errors.append(
            f"{prefix}: tiene {len(item['options'])} opción(es), "
            f"mínimo requerido: {MIN_OPTIONS}"
        )

    # 5. ID: texto no vacío (un número chocaría con su texto al guardarse)
    if not isinstance(item["id"], str) or not item["id"].strip():
        errors.append(f"{prefix}: 'id' debe ser un texto no vacío, es {item['id']!r}")

    # 5b. tags, si está: lista de textos no vacíos
    if "tags" in item:
        tags = item["tags"]
        if not isinstance(tags, list) or not all(isinstance(t, str) and t.strip() for t in tags):
            errors.append(f"{prefix}: 'tags' debe ser una lista de textos no vacíos: {tags!r}")

    # 5c. La imagen, si está, existe (ruta relativa a la raíz del repositorio)
    image = item.get("image_url") or item.get("image_path")
    if image is not None:
        if not isinstance(image, str) or not image.strip():
            errors.append(f"{prefix}: la imagen debe ser una ruta de texto, es {image!r}")
        elif not image.startswith(("http://", "https://")) and not Path(image).is_file():
            errors.append(f"{prefix}: la imagen '{image}' no existe")

    # 6. Content no vacío
    if not str(item.get("content", "")).strip():
        errors.append(f"{prefix}: 'content' está vacío")

    # 7. `topic` nombra la fila del rating (R15): texto no vacío
    if not isinstance(item["topic"], str) or not item["topic"].strip():
        errors.append(f"{prefix}: 'topic' debe ser un texto no vacío, es {item['topic']!r}")

    # 7b. `subtopic`, si está: texto no vacío; solo para estudio, nunca la fila del rating
    #     (spec 008 FR-040)
    if "subtopic" in item and (
        not isinstance(item["subtopic"], str) or not item["subtopic"].strip()
    ):
        errors.append(f"{prefix}: 'subtopic' debe ser un texto no vacío, es {item['subtopic']!r}")

    # 7c. `retired`, si está: un booleano JSON (spec 008 FR-030, O-IL12). Un ítem retirado se
    #     valida completo: puede volver (FR-033) y el historial lo muestra.
    if "retired" in item and type(item["retired"]) is not bool:
        errors.append(f"{prefix}: 'retired' debe ser true o false, es {item['retired']!r}")

    # 8. Ni caracteres de control (R5) ni prosa entre dos `$` (se vería como una fórmula ilegible)
    texts = [item["content"]] + (item["options"] if isinstance(item["options"], list) else [])
    for text in (t for t in texts if isinstance(t, str)):
        for char in control_characters(text):
            errors.append(
                f"{prefix}: carácter de control {char} en {text[:40]!r}; en el JSON el LaTeX lleva "
                "dos barras (R5: \\\\frac, \\\\beta)"
            )
        for token in prose_read_as_math(text):
            errors.append(
                f"{prefix}: {token[:60]!r} se muestra como fórmula; escribe los montos sin $ "
                "(p. ej. '10 millones de pesos')"
            )


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


def validate_manifest(bank_entries: list) -> None:
    """Spec 008 FR-011: the bank against `items/id_manifest.json` (O-V6, O-V8)."""
    if not MANIFEST.is_file():
        errors.append(
            f"no existe {MANIFEST}: sin él nada impide que un id cambie de curso o de tema "
            "(spec 008 FR-011); restáuralo desde git, o en un banco nuevo créalo con "
            f"{rules.MANIFEST_SCRIPT}"
        )
        return
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        errors.append(f"[{MANIFEST}]: JSON inválido: {e}")
        return
    problem = rules.manifest_format_problem(manifest)
    if problem:
        errors.append(problem)
        return
    errors.extend(f"[{MANIFEST.name}] {p}" for p in rules.manifest_problems(manifest, bank_entries))


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
    bank_entries = []  # (id, course, topic): what the manifest records
    total_items = 0

    for json_file in json_files:
        items = validate_file(json_file)
        for item in items:
            validate_item(item, json_file.name)
            if "id" in item:
                all_items.append((str(item["id"]), json_file.name))
            if isinstance(item.get("id"), str) and isinstance(item.get("topic"), str):
                bank_entries.append((item["id"], json_file.stem, item["topic"]))
        total_items += len(items)

    # ── Un tema con menos de 5 ítems: aviso, no error (spec 008 FR-043) ──────
    for json_file in json_files:
        topics = Counter(
            item["topic"]
            for item in validate_file(json_file)
            if isinstance(item.get("topic"), str)
            and item["topic"].strip()
            and item.get("retired") is not True  # a retired item carries no rating (O-IL12)
        )
        for topic, count in sorted(topics.items()):
            if count < SMALL_TOPIC:
                warnings.append(
                    f"[{json_file.name}]: el tema '{topic}' tiene {count} ítem(s); con menos de "
                    f"{SMALL_TOPIC} su rating descansa en pocas respuestas (FR-043)"
                )

    # ── Cada archivo es un curso del catálogo, con bloque y nombre (spec 008 C) ─
    errors.extend(
        catalogue.catalogue_problems(f.relative_to(BANK_DIR).as_posix() for f in json_files)
    )

    # ── Ningún id cambia de curso ni de tema (spec 008 FR-011, D4) ───────────
    validate_manifest(bank_entries)

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
