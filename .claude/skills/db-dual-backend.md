---
name: db-dual-backend
description: >
  Guía crítica para modificar la base de datos de LevelUp-ELO. Usar SIEMPRE
  que la tarea involucre: repositorios (sqlite_repository.py, postgres_repository.py),
  tablas, migraciones, seeds, queries SQL, connection pool, columnas nuevas,
  índices, o cualquier cambio de esquema. También usar al agregar cursos nuevos
  (_COURSE_BLOCK_MAP) o al crear nuevos métodos de acceso a datos.
  NUNCA modificar un repositorio sin consultar esta skill primero.
---

# Skill: db-dual-backend

## Principio fundamental

LevelUp-ELO tiene **dos repositorios con API pública idéntica**:

| Archivo | Backend | Entorno |
|---|---|---|
| `src/infrastructure/persistence/sqlite_repository.py` | SQLite | Desarrollo local |
| `src/infrastructure/persistence/postgres_repository.py` | PostgreSQL (Supabase) | Producción |

**Regla de oro: si cambias uno, cambias el otro.** Sin excepciones. Un repo que difiere del otro es un bug silencioso que explota en producción.

---

## Checklist antes de cualquier modificación

Antes de escribir una sola línea en cualquier repositorio:

- [ ] ¿Cuál es el cambio exacto que voy a hacer?
- [ ] ¿Lo apliqué en `sqlite_repository.py`?
- [ ] ¿Lo apliqué en `postgres_repository.py`?
- [ ] Si agregué una columna, ¿la migración usa `ADD COLUMN IF NOT EXISTS`?
- [ ] Si modifiqué `_COURSE_BLOCK_MAP`, ¿lo sincronicé en ambos archivos?
- [ ] Si toqué el pool de conexiones, ¿usé `put_connection()` y no `close()`?

---

## Diferencias de sintaxis entre backends

Aplicar la sintaxis correcta en cada archivo:

| Concepto | SQLite | PostgreSQL |
|---|---|---|
| Placeholder | `?` | `%s` |
| Autoincremento | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| Upsert | `INSERT OR IGNORE` | `INSERT ... ON CONFLICT DO NOTHING` |
| Booleanos | `0` / `1` (integer) | `TRUE` / `FALSE` |
| Binario (imágenes) | `BLOB` | `BYTEA` |
| Fecha actual | `datetime('now')` | `NOW()` |
| Columna condicional | `ALTER TABLE t ADD COLUMN IF NOT EXISTS` | igual |
| Cursor | `sqlite3.Row` → acceso por nombre | `RealDictCursor` → acceso por nombre |

### Ejemplo: insertar un registro

**SQLite:**
```python
cursor.execute(
    "INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)",
    (username, role)
)
```

**PostgreSQL:**
```python
cursor.execute(
    "INSERT INTO users (username, role) VALUES (%s, %s) ON CONFLICT DO NOTHING",
    (username, role)
)
```

---

## Reglas del pool de conexiones (PostgreSQL)

El repo PostgreSQL usa `SimpleConnectionPool(minconn=1, maxconn=5)`.

**LÍMITE CRÍTICO:** Supabase free tier limita las conexiones del pooler. NUNCA subir `maxconn` a más de 5 — causa `MaxClientsInSessionMode: max clients reached`.

```python
# CORRECTO — siempre devolver la conexión al pool
conn = self.get_connection()
try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT ...")
    result = cursor.fetchall()
    conn.commit()
    return result
except Exception as e:
    conn.rollback()
    raise
finally:
    self.put_connection(conn)   # ← CRÍTICO: siempre en el finally

# INCORRECTO — nunca hacer esto
conn.close()   # destruye la conexión, agota el pool
```

---

## Acceso a filas (PostgreSQL)

PostgreSQL usa `RealDictCursor`. Las filas son diccionarios, no tuplas.

```python
# CORRECTO
username = row['username']
created_at = str(row['created_at'])[:10]   # datetime → string antes de slicear

# INCORRECTO
username = row[0]           # IndexError o valor incorrecto
created_at = row['created_at'][:10]   # AttributeError: datetime no soporta slicing
```

---

## Migraciones: solo aditivas

**Regla absoluta**: las migraciones nunca eliminan ni modifican columnas existentes. Solo agregan.

```python
# CORRECTO
cursor.execute(
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS rating_deviation REAL DEFAULT 350"
)

# JAMÁS hacer esto
cursor.execute("DROP COLUMN old_field")          # rompe datos de producción
cursor.execute("ALTER TABLE users RENAME ...")   # idem
```

### Estructura de una migración nueva

Agregar en `_migrate_db()` de **ambos** repositorios:

```python
# SQLite
try:
    cursor.execute(
        "ALTER TABLE items ADD COLUMN IF NOT EXISTS nueva_columna TEXT DEFAULT ''"
    )
except Exception:
    pass  # columna ya existe — ignorar

# PostgreSQL (con retry)
for attempt in range(3):
    try:
        cursor.execute(
            "ALTER TABLE items ADD COLUMN IF NOT EXISTS nueva_columna TEXT DEFAULT ''"
        )
        conn.commit()
        break
    except (DeadlockDetected, QueryCanceled):
        conn.rollback()
        if attempt < 2:
            time.sleep(2)
```

---

## Agregar un curso nuevo

Este proceso toca ambos repositorios. Seguir en orden:

1. Crear `items/bank/mi_curso.json` (ver skill `items-bank.md` para el formato).

2. En `sqlite_repository.py` → buscar `_COURSE_BLOCK_MAP` y agregar:
   ```python
   'mi_curso': 'Universidad',   # o 'Colegio' o 'Concursos'
   ```

3. En `postgres_repository.py` → buscar `_COURSE_BLOCK_MAP` y agregar la **misma** entrada.

4. Verificar que el slug del archivo (`mi_curso`) coincide exactamente con la clave del mapa.

5. Reiniciar la app — `sync_items_from_bank_folder()` registra el curso en el arranque.

---

## Seed de datos: idempotencia obligatoria

Todo seed debe ser seguro de ejecutar múltiples veces sin duplicar datos ni sobrescribir ELO existente.

```python
# CORRECTO — verificar antes de insertar
cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
if not cursor.fetchone():
    cursor.execute("INSERT INTO users ...")

# TAMBIÉN CORRECTO — usar INSERT OR IGNORE / ON CONFLICT DO NOTHING
cursor.execute(
    "INSERT OR IGNORE INTO users (username, ...) VALUES (?, ...)",
    (username, ...)
)
```

---

## Secuencia de inicialización

Ambos repos ejecutan esto en `__init__`:

```
init_db()
  └→ _migrate_db()          # migraciones aditivas (con pg_advisory_lock en PostgreSQL)
  └→ _seed_admin()          # solo si ADMIN_PASSWORD está en env
  └→ _seed_demo_data()      # datos de demostración
  └→ _backfill_prob_failure() # backfill de columna prob_failure
  └→ sync_items_from_bank_folder()  # sincroniza items/bank/ con DB
  └→ _seed_test_students()  # 5 estudiantes de prueba (idempotente)
```

**PostgreSQL:** Streamlit ejecuta múltiples instancias en paralelo. `_migrate_db()` usa `pg_advisory_lock(12345)` para que solo una instancia ejecute las migraciones. Sin esto → deadlocks.

Al agregar un paso nuevo a esta secuencia, agregarlo en **ambos** repos.

---

## Usuarios de prueba protegidos

Los estudiantes con `is_test_user=1` no pueden borrarse. Nunca escribir queries que ignoren este flag:

```python
# CORRECTO — respetar el flag
cursor.execute(
    "DELETE FROM users WHERE id = ? AND is_test_user = 0", (user_id,)
)

# INCORRECTO — borra usuarios protegidos
cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
```

---

## Tablas de referencia

Esquema completo para no necesitar leer el archivo completo:

```sql
users         (id, username, password_hash, role, approved, active, group_id,
               education_level, is_test_user, rating_deviation, created_at)

groups        (id, teacher_id, name, name_normalized)
              -- UNIQUE(teacher_id, name_normalized)

items         (id, course_id, content, difficulty, rating_deviation,
               topic, options, correct_option, image_url)

attempts      (id, user_id, item_id, is_correct, elo_before, elo_after,
               prob_failure, expected_score, time_taken, confidence_score,
               error_type, rating_deviation, created_at)

courses       (id, name, block)
enrollments   (user_id, course_id, group_id)

procedure_submissions
              (id, user_id, item_id, image_data, storage_url,
               procedure_image_path, mime_type, status, ai_proposed_score,
               teacher_score, final_score, elo_delta, file_hash,
               teacher_comment, feedback_image, feedback_image_path,
               created_at, reviewed_at, seen_by_student)
              -- storage_url = path relativo en Supabase Storage (ej: "38/alb31/hash.jpg")
              -- image_data = BYTEA fallback si Storage falla
              -- procedure_image_path = ruta local legacy (solo SQLite dev)
              -- NUNCA dejar storage_url e image_data ambos en NULL

audit_group_changes
              (id, user_id, old_group_id, new_group_id, changed_by, created_at)
```

---

## Supabase Storage (archivos de procedimientos)

Los archivos que suben los estudiantes (imágenes/PDFs de procedimientos) se almacenan en Supabase Storage, NO en la base de datos.

### Archivo clave
`src/infrastructure/storage/supabase_storage.py` — clase `SupabaseStorage`

### Reglas críticas

**1. upload_file() retorna SOLO el path relativo:**
```python
# CORRECTO — retorna solo el path
return path  # "38/alb31/hash.jpg"

# INCORRECTO — retorna URL completa (NO funciona, bucket es privado)
return storage.get_public_url(path)  # "https://xxx.supabase.co/storage/v1/..."
```

**2. extract_path() debe manejar datos legacy:**
La DB puede contener URLs completas de versiones anteriores del código. `extract_path()` debe limpiarlas:
```python
# Caso 1: URL completa legacy
"https://xxx.supabase.co/storage/v1/object/public/procedimientos/38/alb31/hash.jpg"
→ "38/alb31/hash.jpg"

# Caso 2: Path con nombre de bucket
"procedimientos/38/alb31/hash.jpg"
→ "38/alb31/hash.jpg"

# Caso 3: Path limpio (ya correcto)
"38/alb31/hash.jpg"
→ "38/alb31/hash.jpg"
```

**3. Fallback obligatorio a BYTEA:**
Si el upload a Storage falla, `save_procedure_submission()` DEBE guardar los bytes en `image_data`. Nunca dejar ambos campos en NULL.

**4. Mostrar imágenes — descargar bytes:**
El bucket es PRIVADO. No usar URLs directas con `st.image()`. Siempre descargar bytes:
```python
# CORRECTO
img_bytes = repo.resolve_storage_image(storage_url)
if img_bytes:
    st.image(img_bytes)

# INCORRECTO — URLs públicas no funcionan en bucket privado
st.image(storage_url)
```

**5. resolve_storage_image() existe en ambos repos:**
- `postgres_repository.py` → descarga desde Supabase Storage vía `self._storage.get_file()`
- `sqlite_repository.py` → stub que retorna `None` (en local los archivos están en disco)

### Variables de entorno
```
SUPABASE_URL=https://lcgnmdpsjvfqbnzmgjzt.supabase.co
SUPABASE_KEY=sb_publishable_POX4...
```
Configuradas en `.env` (local) y Streamlit Cloud → Settings → Secrets (producción).
