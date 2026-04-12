#!/usr/bin/env python3
"""
db_sync_check.py — Verificador de consistencia entre repositorios de LevelUp-ELO.

Uso:
    python scripts/db_sync_check.py
    python scripts/db_sync_check.py --fix   # intenta corregir diferencias simples

Ejecutar desde la raíz del repo.
"""

import ast
import re
import sys
from pathlib import Path

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


def get_public_methods(source: str) -> dict[str, str]:
    """Retorna {nombre_método: firma_completa} para métodos públicos."""
    methods = {}
    for m in re.finditer(r"^\s{4}def ([a-z][^_][^(]*)\(([^)]*)\)", source, re.MULTILINE):
        name = m.group(1).strip()
        params = m.group(2).strip()
        methods[name] = params
    return methods


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


def get_migrations(source: str) -> list[str]:
    """Extrae operaciones DDL del bloque _migrate_db."""
    lines = []
    in_migrate = False
    for line in source.splitlines():
        if "def _migrate_db" in line:
            in_migrate = True
        elif in_migrate and re.match(r"    def ", line):
            break
        if in_migrate:
            if re.search(r"ALTER TABLE|ADD COLUMN|CREATE TABLE|CREATE INDEX", line):
                # normalizar para comparación
                clean = re.sub(r"\s+", " ", line.strip())
                clean = re.sub(r"['\"]", "", clean)
                lines.append(clean)
    return lines


# ─── Verificaciones ───────────────────────────────────────────────────────────


def check_methods(sqlite_src: str, pg_src: str):
    print(f"\n{BOLD}1. Métodos públicos{RESET}")
    sqlite_methods = get_public_methods(sqlite_src)
    pg_methods = get_public_methods(pg_src)

    # Excluir helpers internos del pool de conexiones (solo en PostgreSQL)
    _PG_INTERNAL = {"put_connection", "get_connection", "decorator", "wrapper"}
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

    # Verificar firmas de métodos compartidos
    mismatched = []
    for name in sorted(in_both):
        s_params = re.sub(r"\s+", " ", sqlite_methods[name])
        p_params = re.sub(r"\s+", " ", pg_methods[name])
        if s_params != p_params:
            mismatched.append(f"{name}(): SQLite({s_params}) vs PG({p_params})")

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
    print(f"\n{BOLD}3. Migraciones (_migrate_db){RESET}")
    sqlite_migs = get_migrations(sqlite_src)
    pg_migs = get_migrations(pg_src)

    check(
        "Mismo número de operaciones DDL",
        len(sqlite_migs) == len(pg_migs),
        f"SQLite: {len(sqlite_migs)} operaciones | PG: {len(pg_migs)} operaciones",
    )

    if len(sqlite_migs) != len(pg_migs):
        extra_sqlite = [
            m
            for m in sqlite_migs
            if not any(re.sub(r"[\?\%]s", "X", m) in re.sub(r"[\?\%]s", "X", p) for p in pg_migs)
        ]
        extra_pg = [
            m
            for m in pg_migs
            if not any(
                re.sub(r"[\?\%]s", "X", p) in re.sub(r"[\?\%]s", "X", s) for s in sqlite_migs
            )
        ]
        if extra_sqlite:
            warn("Migraciones en SQLite sin equivalente en PG:", "\n       ".join(extra_sqlite[:3]))
        if extra_pg:
            warn("Migraciones en PG sin equivalente en SQLite:", "\n       ".join(extra_pg[:3]))


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
    print(f"\n{BOLD}{'═'*55}{RESET}")
    print(f"{BOLD}  DB SYNC CHECK — LevelUp-ELO{RESET}")
    print(f"{BOLD}{'═'*55}{RESET}")
    print(f"  SQLite:     {SQLITE_PATH}")
    print(f"  PostgreSQL: {POSTGRES_PATH}")

    sqlite_src = read(SQLITE_PATH)
    pg_src = read(POSTGRES_PATH)

    check_methods(sqlite_src, pg_src)
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
