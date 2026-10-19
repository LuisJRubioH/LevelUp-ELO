#!/usr/bin/env python3
"""
db_sync_check.py — Verificador de consistencia entre repositorios de LevelUp-ELO.

Uso:
    python scripts/db_sync_check.py
    python scripts/db_sync_check.py --sqlite PATH --postgres PATH   # otras copias (tests)

Ejecutar desde la raíz del repo.

Spec 002 D3: las secciones 1 (firmas, con inspect) y 3 (esquema, con ast sobre cada método de
migración) fallan ante cualquier diferencia que no esté aceptada en
src/infrastructure/persistence/engine_differences.py, y ante una aceptada que ya no exista.
"""

import argparse
import ast
import importlib.util
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SQLITE_PATH = Path("src/infrastructure/persistence/sqlite_repository.py")
POSTGRES_PATH = Path("src/infrastructure/persistence/postgres_repository.py")

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

errors = []
warnings = []


def check(label: str, ok: bool, detail: str = ""):
    symbol = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
    print(f"  {symbol}  {label}")
    if not ok and detail:
        print(f"       {RED}{detail}{RESET}")
    if not ok:
        errors.append(f"{label}: {detail}" if detail else label)


def warn(label: str, detail: str = ""):
    print(f"  {YELLOW}⚠{RESET}  {label}")
    if detail:
        print(f"       {YELLOW}{detail}{RESET}")
    warnings.append(label)


# ─── Lectura de archivos ──────────────────────────────────────────────────────


def read(path: Path) -> str:
    if not path.exists():
        print(f"{RED}ERROR: No se encontró {path}{RESET}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def get_course_block_map(source: str) -> dict[str, str]:
    """Extrae _COURSE_BLOCK_MAP como diccionario."""
    m = re.search(r"_COURSE_BLOCK_MAP\s*=\s*\{([^}]+)\}", source, re.DOTALL)
    if not m:
        return {}
    pairs = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"\s*['\"](\w+)['\"]\s*:\s*['\"]([^'\"]+)['\"]", line)
        if kv:
            pairs[kv.group(1)] = kv.group(2)
    return pairs


_CONSTRAINT_WORDS = {"PRIMARY", "UNIQUE", "FOREIGN", "CHECK", "CONSTRAINT"}
_CREATE_TABLE = re.compile(r"CREATE TABLE (?:IF NOT EXISTS )?(\w+)\s*\((.*)\)", re.DOTALL)
_CREATE_INDEX = re.compile(
    r"CREATE (UNIQUE )?INDEX (?:IF NOT EXISTS )?(\w+)\s+ON\s+(\w+)\s*\(([^)]*)\)"
)


def _top_level_parts(body: str) -> list[str]:
    parts, depth, current = [], 0, ""
    for char in body:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
    return parts + [current]


def _loop_values(method) -> dict:
    """{name: [values]} for `for a, b in ((..., ...), ...)` loops over literal tuples."""
    values = {}
    for node in ast.walk(method):
        if not isinstance(node, ast.For) or not isinstance(node.iter, (ast.Tuple, ast.List)):
            continue
        targets = node.target.elts if isinstance(node.target, ast.Tuple) else [node.target]
        for position, target in enumerate(targets):
            if not isinstance(target, ast.Name):
                continue
            column = []
            for element in node.iter.elts:
                item = element.elts[position] if isinstance(element, ast.Tuple) else element
                if isinstance(item, ast.Constant):
                    column.append(item.value)
            values[target.id] = column
    return values


def static_catalogue(source: str, class_name: str):
    """Tables, columns and indexes the migration methods of one repository create (spec 002
    FR-040): read from their code, so no database is needed."""
    from src.infrastructure.persistence.engine_differences import Catalogue
    from src.infrastructure.persistence.schema_version import _MIGRATION_METHODS

    tree = ast.parse(source)
    (cls,) = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name]
    catalogue = Catalogue()
    index_names = set()
    for method in cls.body:
        if not isinstance(method, ast.FunctionDef) or method.name not in _MIGRATION_METHODS:
            continue
        loops = _loop_values(method)
        docstring = ast.get_docstring(method, clean=False)
        for node in ast.walk(method):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value == docstring:
                    continue
                sql = re.sub(r"\s+", " ", node.value).strip()
                table = _CREATE_TABLE.search(sql)
                if table:
                    catalogue.add_table(table.group(1))
                    for part in _top_level_parts(table.group(2)):
                        word = part.strip().split(" ")[0] if part.strip() else ""
                        if word and word.upper() not in _CONSTRAINT_WORDS:
                            catalogue.add_column(table.group(1), word)
                index = _CREATE_INDEX.search(sql)
                # One index per name: `CREATE INDEX IF NOT EXISTS` twice makes one index.
                if index and index.group(2) not in index_names:
                    index_names.add(index.group(2))
                    columns = [c.strip().split(" ")[0] for c in index.group(4).split(",")]
                    catalogue.add_index(index.group(3), columns, bool(index.group(1)))
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "_add_column_if_not_exists"
                and len(node.args) >= 3
            ):
                tables, columns = (
                    (
                        [arg.value]
                        if isinstance(arg, ast.Constant)
                        else loops.get(getattr(arg, "id", ""), [])
                    )
                    for arg in node.args[1:3]
                )
                for table in tables:
                    for column in columns:
                        catalogue.add_column(table, column)
    return catalogue


def load_class(path: Path, class_name: str):
    """Imports a repository module from a path (the real file, or a test's edited copy)."""
    spec = importlib.util.spec_from_file_location(f"_db_sync_{class_name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def public_signatures(cls) -> dict:
    """{method: [(parameter, kind, default)]} for every public method."""
    return {
        name: [
            (p.name, p.kind.name, repr(p.default))
            for p in inspect.signature(fn).parameters.values()
        ]
        for name, fn in inspect.getmembers(cls, inspect.isfunction)
        if not name.startswith("_")
    }


# ─── Verificaciones ───────────────────────────────────────────────────────────


def check_methods(sqlite_path: Path, pg_path: Path):
    """FR-041: the same public methods with the same parameters (names, kinds, defaults),
    read with inspect from the imported classes."""
    print(f"\n{BOLD}1. Métodos públicos{RESET}")
    sqlite_methods = public_signatures(load_class(sqlite_path, "SQLiteRepository"))
    pg_methods = public_signatures(load_class(pg_path, "PostgresRepository"))

    # put_connection devuelve la conexión al pool: solo existe en PostgreSQL.
    _PG_INTERNAL = {"put_connection"}
    only_sqlite = set(sqlite_methods) - set(pg_methods) - _PG_INTERNAL
    only_pg = set(pg_methods) - set(sqlite_methods) - _PG_INTERNAL
    in_both = set(sqlite_methods) & set(pg_methods)

    check(
        "Todos los métodos presentes en ambos repos",
        not only_sqlite and not only_pg,
        (
            f"Solo en SQLite: {sorted(only_sqlite)} | Solo en PG: {sorted(only_pg)}"
            if only_sqlite or only_pg
            else ""
        ),
    )

    mismatched = [
        f"{name}(): SQLite{sqlite_methods[name]} vs PG{pg_methods[name]}"
        for name in sorted(in_both)
        if sqlite_methods[name] != pg_methods[name]
    ]
    check(
        "Firmas de métodos coinciden",
        not mismatched,
        " | ".join(mismatched[:3]) + (" ..." if len(mismatched) > 3 else ""),
    )

    return only_sqlite, only_pg


def check_course_map(sqlite_src: str, pg_src: str):
    print(f"\n{BOLD}2. _COURSE_BLOCK_MAP{RESET}")
    sqlite_map = get_course_block_map(sqlite_src)
    pg_map = get_course_block_map(pg_src)

    only_sqlite = {k: v for k, v in sqlite_map.items() if k not in pg_map}
    only_pg = {k: v for k, v in pg_map.items() if k not in sqlite_map}
    conflicts = {k for k in sqlite_map if k in pg_map and sqlite_map[k] != pg_map[k]}

    check("_COURSE_BLOCK_MAP presente en ambos repos", bool(sqlite_map) and bool(pg_map))
    check(
        "Mismas claves en ambos mapas",
        not only_sqlite and not only_pg,
        f"Solo en SQLite: {only_sqlite} | Solo en PG: {only_pg}" if only_sqlite or only_pg else "",
    )
    check(
        "Sin conflictos de valor",
        not conflicts,
        f"Claves con valores distintos: {conflicts}" if conflicts else "",
    )


def check_migrations(sqlite_src: str, pg_src: str):
    """FR-040: tables, columns and indexes created by every migration method, both engines."""
    from src.infrastructure.persistence.engine_differences import unexplained

    print(f"\n{BOLD}3. Esquema de las migraciones{RESET}")
    sqlite = static_catalogue(sqlite_src, "SQLiteRepository")
    postgres = static_catalogue(pg_src, "PostgresRepository")
    problems = unexplained(sqlite, postgres, runtime=False)
    check(
        f"Mismas tablas, columnas e índices ({len(postgres.tables)} tablas) salvo las "
        "diferencias aceptadas",
        not problems,
        "\n       ".join(problems),
    )


def check_placeholders(sqlite_src: str, pg_src: str):
    print(f"\n{BOLD}4. Placeholders SQL{RESET}")

    # SQLite no debe tener %s en queries
    sqlite_bad = [
        f"línea {i+1}: {l.strip()}"
        for i, l in enumerate(sqlite_src.splitlines())
        if "%s" in l and "execute" in l and not l.strip().startswith("#")
    ]
    check("SQLite usa ? (no %s)", not sqlite_bad, " | ".join(sqlite_bad[:2]))

    # PostgreSQL no debe tener ? en queries (excepto en strings/comentarios)
    pg_bad = [
        f"línea {i+1}: {l.strip()}"
        for i, l in enumerate(pg_src.splitlines())
        if re.search(r"execute\([^)]*\?", l) and not l.strip().startswith("#")
    ]
    check("PostgreSQL usa %s (no ?)", not pg_bad, " | ".join(pg_bad[:2]))


def check_row_access(pg_src: str):
    print(f"\n{BOLD}5. Acceso a filas (PostgreSQL){RESET}")

    bad_index = [
        f"línea {i+1}: {l.strip()}"
        for i, l in enumerate(pg_src.splitlines())
        if re.search(r"\brow\s*\[\s*\d+\s*\]", l) and not l.strip().startswith("#")
    ]
    check("Sin acceso por índice numérico (row[0])", not bad_index, " | ".join(bad_index[:3]))

    date_slices = [
        f"línea {i+1}: {l.strip()}"
        for i, l in enumerate(pg_src.splitlines())
        if re.search(r"row\[['\"][^'\"]*date[^'\"]*['\"]\]\[:10\]", l)
        and "str(" not in l
        and not l.strip().startswith("#")
    ]
    check(
        "Fechas envueltas en str() antes de slicear",
        not date_slices,
        "Usar str(row['created_at'])[:10] no row['created_at'][:10]" if date_slices else "",
    )


def check_connection_pool(pg_src: str):
    print(f"\n{BOLD}6. Pool de conexiones (PostgreSQL){RESET}")

    conn_close = [
        f"línea {i+1}: {l.strip()}"
        for i, l in enumerate(pg_src.splitlines())
        if "conn.close()" in l and not l.strip().startswith("#")
    ]
    check("Sin conn.close() (usar put_connection())", not conn_close, " | ".join(conn_close[:3]))

    # Verificar que todo get_connection() tiene put_connection() en finally
    get_count = pg_src.count("self.get_connection()")
    put_count = pg_src.count("self.put_connection(")
    check(
        "get_connection() y put_connection() balanceados",
        abs(get_count - put_count) <= 1,
        (
            f"get_connection: {get_count} veces | put_connection: {put_count} veces"
            if abs(get_count - put_count) > 1
            else ""
        ),
    )


def check_idempotent_seeds(sqlite_src: str, pg_src: str):
    print(f"\n{BOLD}7. Seeds idempotentes{RESET}")

    for name, src in [("SQLite", sqlite_src), ("PostgreSQL", pg_src)]:
        # Buscar inserts sin guard de existencia
        raw_inserts = re.findall(r'cursor\.execute\(["\']INSERT INTO \w+[^"\']*["\']', src)
        unsafe = [i for i in raw_inserts if "OR IGNORE" not in i and "ON CONFLICT" not in i]
        if unsafe:
            warn(
                f"{name}: {len(unsafe)} INSERT sin idempotencia",
                "Considerar INSERT OR IGNORE / ON CONFLICT DO NOTHING",
            )
        else:
            print(f"  {GREEN}✓{RESET}  {name}: seeds idempotentes")


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    global SQLITE_PATH, POSTGRES_PATH
    parser = argparse.ArgumentParser(description="Paridad SQLite/PostgreSQL (AGENTS R1).")
    parser.add_argument("--sqlite", type=Path, default=SQLITE_PATH)
    parser.add_argument("--postgres", type=Path, default=POSTGRES_PATH)
    args = parser.parse_args()
    SQLITE_PATH, POSTGRES_PATH = args.sqlite, args.postgres
    print(f"\n{BOLD}{'═'*55}{RESET}")
    print(f"{BOLD}  DB SYNC CHECK — LevelUp-ELO{RESET}")
    print(f"{BOLD}{'═'*55}{RESET}")
    print(f"  SQLite:     {SQLITE_PATH}")
    print(f"  PostgreSQL: {POSTGRES_PATH}")

    sqlite_src = read(SQLITE_PATH)
    pg_src = read(POSTGRES_PATH)

    check_methods(SQLITE_PATH, POSTGRES_PATH)
    check_course_map(sqlite_src, pg_src)
    check_migrations(sqlite_src, pg_src)
    check_placeholders(sqlite_src, pg_src)
    check_row_access(pg_src)
    check_connection_pool(pg_src)
    check_idempotent_seeds(sqlite_src, pg_src)

    print(f"\n{BOLD}{'─'*55}{RESET}")

    if not errors and not warnings:
        print(f"{GREEN}{BOLD}  ✓ REPOS EN SYNC — seguro para commit{RESET}")
        return 0

    if warnings and not errors:
        print(f"{YELLOW}{BOLD}  ⚠ {len(warnings)} advertencia(s) — revisar antes de commit{RESET}")
        return 0

    print(f"{RED}{BOLD}  ✗ {len(errors)} error(es) encontrado(s) — NO hacer commit{RESET}")
    print(f"\n{BOLD}  Errores:{RESET}")
    for e in errors:
        print(f"    {RED}•{RESET} {e}")

    if warnings:
        print(f"\n{BOLD}  Advertencias:{RESET}")
        for w in warnings:
            print(f"    {YELLOW}•{RESET} {w}")

    print(f"{BOLD}{'═'*55}{RESET}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
