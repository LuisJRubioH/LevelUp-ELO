# Prompt para Claude Code — Nivel Educativo "Semillero de Matemáticas"

## Rol
Actúa como desarrollador full-stack experto en Python/Streamlit con dominio de Clean Architecture y dual-backend SQLite/PostgreSQL.

## Contexto
- Proyecto: **ELO** (plataforma adaptativa de práctica matemática con sistema ELO)
- Stack: Python + Streamlit, SQLite (local) / PostgreSQL-Supabase (producción)
- Arquitectura: Clean Architecture en `src/` (domain → application → infrastructure → interface)
- UI monolítica: `src/interface/streamlit/app.py`
- Dual backend: `sqlite_repository.py` + `postgres_repository.py` con API idéntica
- Niveles educativos actuales: `universidad`, `colegio`, `concursos`
- Mapeo curso→bloque: `_COURSE_BLOCK_MAP` en **ambos** repositorios
- Rankings ya filtran por `education_level`

**OBLIGATORIO antes de empezar:** Lee las skills del proyecto:
- `.claude/skills/db-dual-backend.md`
- `.claude/skills/clean-architecture.md`
- `.claude/skills/items-bank.md`
- Al finalizar: `.claude/skills/db-sync-checker.md` + ejecutar `python scripts/db_sync_check.py`

## Objetivo
Agregar un 4° nivel educativo **`semillero`** con selección de grado (6°–11° bachillerato) y 6 materias de preparación para Olimpiadas Matemáticas UdeA. Rankings separados por grado dentro del nivel Semillero.

## Alcance

### INCLUIR:

#### 1. Base de datos (ambos repositorios)
- Agregar columna `grade` (TEXT, nullable) a tabla `users` — migración aditiva `ALTER TABLE ADD COLUMN IF NOT EXISTS`
- `grade` solo aplica cuando `education_level = 'semillero'`; valores válidos: `'6'`, `'7'`, `'8'`, `'9'`, `'10'`, `'11'`
- Agregar `'semillero'` como valor válido de `education_level`

#### 2. Catálogo de cursos (`_COURSE_BLOCK_MAP` en AMBOS repos)
Agregar estas 6 entradas:
```python
'aritmetica_semillero': 'Semillero',
'algebra_semillero': 'Semillero',
'geometria_semillero': 'Semillero',
'logica_semillero': 'Semillero',
'conteo_combinatoria_semillero': 'Semillero',
'probabilidad_semillero': 'Semillero',
```

#### 3. Bancos de preguntas (6 archivos JSON en `items/bank/`)
Crear archivos con estructura mínima válida (1 ítem placeholder cada uno) para que el sistema los reconozca al arrancar:
- `items/bank/aritmetica_semillero.json`
- `items/bank/algebra_semillero.json`
- `items/bank/geometria_semillero.json`
- `items/bank/logica_semillero.json`
- `items/bank/conteo_combinatoria_semillero.json`
- `items/bank/probabilidad_semillero.json`

Formato de cada ítem placeholder:
```json
[
  {
    "id": "<slug>_001",
    "content": "Pregunta placeholder — reemplazar con contenido real.",
    "difficulty": 1000,
    "topic": "<Nombre de la materia>",
    "options": ["A", "B", "C", "D"],
    "correct_option": "A"
  }
]
```

#### 4. UI — Registro (`app.py`)
- Cuando el estudiante selecciona nivel `Semillero de Matemáticas`, mostrar un segundo selector: **"Grado"** con opciones `6°`, `7°`, `8°`, `9°`, `10°`, `11°`
- Guardar el grado en campo `grade` del usuario
- Si el nivel NO es semillero, `grade` debe ser `NULL`

#### 5. UI — Sala de estudio (`app.py`)
- El estudiante con `education_level = 'semillero'` ve el catálogo de cursos del bloque `Semillero` (las 6 materias)
- Mostrar en la sala un encabezado: **"🏅 Semillero de Matemáticas — Olimpiadas UdeA"** con el grado del estudiante
- Todos los grados ven las mismas 6 materias

#### 6. UI — Rankings (`app.py`)
- Agregar `Semillero` como opción en el filtro de nivel educativo para rankings
- **Dentro de Semillero**, agregar sub-filtro por grado (6°–11°)
- El ranking filtra estudiantes por `education_level = 'semillero'` AND `grade = <grado_seleccionado>`
- Aplicar esto tanto en el ranking del estudiante como en el panel de ranking del docente

#### 7. Seed de prueba (`seed_test_students.py`)
Agregar 2 estudiantes de prueba:
| Usuario | Contraseña | Nivel | Grado | Cursos |
|---|---|---|---|---|
| `estudiante_semillero_1` | `test1234` | `semillero` | `9` | Todos los cursos Semillero |
| `estudiante_semillero_2` | `test1234` | `semillero` | `11` | Todos los cursos Semillero |
Ambos con `is_test_user=1`. Seed idempotente (solo crear si no existen).

### EXCLUIR:
- No modificar lógica de ELO, selección adaptativa ni análisis cognitivo
- No crear ítems reales (solo placeholders)
- No modificar el flujo del docente ni del admin (excepto que el docente pueda ver el nuevo nivel en sus filtros)
- No cambiar la estructura de tablas existentes (solo agregar columna `grade`)

## Requisitos técnicos
- Python 3.10+, Streamlit
- Migraciones solo aditivas (`ALTER TABLE ADD COLUMN IF NOT EXISTS`)
- Sincronizar `_COURSE_BLOCK_MAP` en `sqlite_repository.py` Y `postgres_repository.py`
- PostgreSQL: usar `RealDictCursor`, acceso por `row['column_name']`
- Mantener consistencia con convenciones existentes del proyecto
- No romper funcionalidad existente de universidad/colegio/concursos

## Instrucciones de ejecución
1. Leer las 3 skills obligatorias antes de tocar código
2. Crear los 6 archivos JSON en `items/bank/`
3. Modificar `_COURSE_BLOCK_MAP` en ambos repositorios
4. Agregar migración de columna `grade` en ambos repositorios
5. Modificar UI de registro en `app.py` (selector condicional de grado)
6. Modificar sala de estudio para mostrar catálogo Semillero
7. Modificar rankings para incluir filtro Semillero + sub-filtro por grado
8. Actualizar `seed_test_students.py`
9. Ejecutar `python scripts/db_sync_check.py` y corregir cualquier diferencia
10. Actualizar `CLAUDE.md` y `README.md` con la nueva información

## Formato de salida
- Código listo para producción, sin explicaciones
- Modificar archivos existentes in-place
- Crear archivos nuevos donde corresponda
- Al finalizar: listar archivos modificados/creados

## Criterios de calidad
- Ambos backends (SQLite + PostgreSQL) funcionan idénticamente
- `db_sync_check.py` pasa sin errores
- Registro con nivel semillero guarda `grade` correctamente
- Estudiante semillero ve solo las 6 materias del bloque Semillero
- Rankings de Semillero filtran por grado
- Estudiantes de prueba se crean correctamente
- No hay regresiones en los niveles existentes
