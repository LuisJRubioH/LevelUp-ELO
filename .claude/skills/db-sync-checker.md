---
name: db-sync-checker
description: >
  Subagente que verifica la consistencia entre sqlite_repository.py y
  postgres_repository.py en LevelUp-ELO. Invocar después de cualquier
  modificación a uno de los dos repositorios para asegurar que el otro
  está en sync. Detecta columnas faltantes, métodos desincronizados,
  diferencias en _COURSE_BLOCK_MAP, migraciones incompletas y errores
  de sintaxis específicos de cada backend.
---

# Subagente: db-sync-checker

## Propósito

Verificar que `sqlite_repository.py` y `postgres_repository.py` están en sincronía después de un cambio. Actuar como revisión final antes de hacer commit cuando se toca cualquier repositorio.

## Cuándo invocarlo

Claude Code debe invocar este subagente automáticamente cuando:
- Se modifica `sqlite_repository.py`
- Se modifica `postgres_repository.py`
- Se agrega una tabla o columna nueva
- Se agrega un método nuevo a cualquier repo
- Se modifica `_COURSE_BLOCK_MAP`
- Se agrega una migración nueva

---

## Proceso de verificación

### Paso 1 — Leer ambos archivos

```bash
# Obtener lista de métodos públicos en SQLite
grep -n "def " src/infrastructure/persistence/sqlite_repository.py | grep -v "def _"

# Obtener lista de métodos públicos en PostgreSQL
grep -n "def " src/infrastructure/persistence/postgres_repository.py | grep -v "def _"
```

Comparar ambas listas. Cualquier método presente en uno y ausente en el otro es un error.

### Paso 2 — Verificar _COURSE_BLOCK_MAP

```bash
# Extraer el mapa de SQLite
grep -A 30 "_COURSE_BLOCK_MAP" src/infrastructure/persistence/sqlite_repository.py | head -40

# Extraer el mapa de PostgreSQL
grep -A 30 "_COURSE_BLOCK_MAP" src/infrastructure/persistence/postgres_repository.py | head -40
```

Las claves y valores deben ser idénticos en ambos archivos.

### Paso 3 — Verificar migraciones

```bash
# Extraer bloque _migrate_db de SQLite
grep -n "ALTER TABLE\|ADD COLUMN\|CREATE TABLE\|CREATE INDEX" \
  src/infrastructure/persistence/sqlite_repository.py

# Extraer bloque _migrate_db de PostgreSQL
grep -n "ALTER TABLE\|ADD COLUMN\|CREATE TABLE\|CREATE INDEX" \
  src/infrastructure/persistence/postgres_repository.py
```

Cada operación de schema en SQLite debe tener su equivalente en PostgreSQL (con la sintaxis correcta de cada backend).

### Paso 4 — Verificar firmas de métodos públicos

Para cada método público encontrado en el Paso 1, comparar:
- Nombre del método
- Parámetros (nombres y orden)
- Tipo de retorno esperado (por convención del proyecto)

```bash
# Ver firma completa de un método específico en ambos repos
grep -A 3 "def get_user_by_username" src/infrastructure/persistence/sqlite_repository.py
grep -A 3 "def get_user_by_username" src/infrastructure/persistence/postgres_repository.py
```

### Paso 5 — Verificar sintaxis de placeholders

```bash
# SQLite debe usar ? — detectar %s accidentales
grep -n "%s" src/infrastructure/persistence/sqlite_repository.py

# PostgreSQL debe usar %s — detectar ? accidentales (fuera de comentarios)
grep -n "[^']?[^']" src/infrastructure/persistence/postgres_repository.py | grep "execute"
```

### Paso 6 — Verificar acceso a filas

```bash
# PostgreSQL no debe tener acceso por índice numérico
grep -n "row\[0\]\|row\[1\]\|row\[2\]\|fetchone()\[" \
  src/infrastructure/persistence/postgres_repository.py
```

Cualquier resultado es un bug — PostgreSQL usa `RealDictCursor`, acceso solo por nombre.

### Paso 7 — Verificar manejo del pool

```bash
# PostgreSQL no debe tener conn.close()
grep -n "conn\.close()" src/infrastructure/persistence/postgres_repository.py
```

Cualquier `conn.close()` es un bug — usar `self.put_connection(conn)`.

---

## Reporte de resultados

Al terminar la verificación, generar un reporte con este formato:

```
═══════════════════════════════════════════
DB SYNC CHECK — LevelUp-ELO
═══════════════════════════════════════════

✓ / ✗  Métodos públicos sincronizados
✓ / ✗  _COURSE_BLOCK_MAP idéntico
✓ / ✗  Migraciones completas en ambos repos
✓ / ✗  Firmas de métodos coinciden
✓ / ✗  Placeholders correctos (? vs %s)
✓ / ✗  Sin acceso por índice en PostgreSQL
✓ / ✗  Sin conn.close() en PostgreSQL

PROBLEMAS ENCONTRADOS:
─────────────────────
[lista de problemas con archivo:línea y descripción]

ACCIONES REQUERIDAS:
────────────────────
[lista de cambios necesarios para corregir]
```

Si todos los checks pasan → `✓ REPOS EN SYNC — seguro para commit`.
Si hay fallos → listar cada problema con su corrección exacta antes de continuar.

---

## Correcciones automáticas

Para problemas simples y de bajo riesgo, el subagente puede aplicar la corrección directamente:

### Método faltante en PostgreSQL

Si SQLite tiene un método que PostgreSQL no tiene, crear el equivalente en PostgreSQL con:
1. La misma firma (nombre y parámetros)
2. Sintaxis PostgreSQL (`%s` en lugar de `?`, `RealDictCursor`, etc.)
3. Manejo de pool en bloque `try/finally` con `self.put_connection(conn)`

### Método faltante en SQLite

Si PostgreSQL tiene un método que SQLite no tiene, crear el equivalente en SQLite con:
1. La misma firma
2. Sintaxis SQLite (`?`, `sqlite3.Row`, sin pool)

### _COURSE_BLOCK_MAP desincronizado

Copiar la entrada faltante al repo que la no tiene. Si los valores difieren para la misma clave, marcar como conflicto y pedir confirmación del usuario.

### Para problemas complejos (conflictos de lógica, diferencias semánticas)

No auto-corregir. Reportar el problema con claridad y esperar instrucción del usuario.

---

## Diferencias de sintaxis de referencia rápida

| Concepto | SQLite | PostgreSQL |
|---|---|---|
| Placeholder | `?` | `%s` |
| Autoincremento | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| Upsert | `INSERT OR IGNORE` | `INSERT ... ON CONFLICT DO NOTHING` |
| Booleanos | `0` / `1` | `TRUE` / `FALSE` |
| Binario | `BLOB` | `BYTEA` |
| Fecha actual | `datetime('now')` | `NOW()` |
| Cursor | `sqlite3.Row` | `RealDictCursor` |
| Conexión | directa | pool → `put_connection()` |
| Acceso fila | `row['col']` o `row[0]` | `row['col']` solo |
| Fechas | strings | objetos `datetime` → `str()` antes de slicear |

---

## Ejemplo de invocación desde CLAUDE.md

Cuando Claude Code detecta que modificó un repositorio, debe invocar este subagente así:

```
He modificado sqlite_repository.py para agregar el método get_student_streak().
Invocar db-sync-checker para verificar que postgres_repository.py también
tiene el cambio equivalente antes de continuar.
```

El subagente ejecuta los pasos 1–7, genera el reporte, y si hay problemas los corrige o los reporta.
