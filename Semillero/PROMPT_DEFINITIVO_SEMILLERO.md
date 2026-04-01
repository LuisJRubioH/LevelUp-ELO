# Prompt DEFINITIVO — Semillero de Matemáticas completo

## Rol
Desarrollador full-stack Python/Streamlit con dominio de Clean Architecture y dual-backend SQLite/PostgreSQL.

## Contexto
- Proyecto: **ELO** — plataforma adaptativa de práctica matemática
- Stack: Python + Streamlit, SQLite (local) / PostgreSQL-Supabase (producción)
- UI monolítica: `src/interface/streamlit/app.py`
- Dual backend: `sqlite_repository.py` + `postgres_repository.py` con API idéntica
- Niveles educativos actuales: `universidad`, `colegio`, `concursos`
- Mapeo curso→bloque: `_COURSE_BLOCK_MAP` en **ambos** repositorios

**OBLIGATORIO antes de empezar:** Lee las skills:
- `.claude/skills/db-dual-backend.md`
- `.claude/skills/clean-architecture.md`
- `.claude/skills/items-bank.md`
- Al finalizar: `.claude/skills/db-sync-checker.md` + ejecutar `python scripts/db_sync_check.py`

---

## Objetivo

Agregar un 4° nivel educativo **Semillero de Matemáticas** con:
- Selección de grado (6°–11°) al registrarse
- **Cada grado ve SOLO sus propias materias** (36 cursos = 6 materias × 6 grados)
- 106 preguntas reales de Olimpiadas UdeA distribuidas por grado
- Figuras geométricas generadas con matplotlib
- Rankings separados por grado dentro del Semillero

---

## PARTE 1: Base de datos y nivel educativo

### 1.1 Columna `grade` en tabla `users` (ambos repos)
Migración aditiva: `ALTER TABLE users ADD COLUMN IF NOT EXISTS grade TEXT`
- Solo aplica cuando `education_level = 'semillero'`
- Valores válidos: `'6'`, `'7'`, `'8'`, `'9'`, `'10'`, `'11'`
- Si `education_level != 'semillero'`, `grade` es `NULL`

### 1.2 `_COURSE_BLOCK_MAP` en AMBOS repositorios
Agregar estas 35 entradas (6 materias × 6 grados, excepto `aritmetica_semillero_9` que no tiene preguntas aún):

```python
# Semillero 6°
'logica_semillero_6': 'Semillero 6°',
'algebra_semillero_6': 'Semillero 6°',
'geometria_semillero_6': 'Semillero 6°',
'conteo_combinatoria_semillero_6': 'Semillero 6°',
'probabilidad_semillero_6': 'Semillero 6°',
'aritmetica_semillero_6': 'Semillero 6°',
# Semillero 7°
'logica_semillero_7': 'Semillero 7°',
'algebra_semillero_7': 'Semillero 7°',
'geometria_semillero_7': 'Semillero 7°',
'conteo_combinatoria_semillero_7': 'Semillero 7°',
'probabilidad_semillero_7': 'Semillero 7°',
'aritmetica_semillero_7': 'Semillero 7°',
# Semillero 8°
'logica_semillero_8': 'Semillero 8°',
'algebra_semillero_8': 'Semillero 8°',
'geometria_semillero_8': 'Semillero 8°',
'conteo_combinatoria_semillero_8': 'Semillero 8°',
'probabilidad_semillero_8': 'Semillero 8°',
'aritmetica_semillero_8': 'Semillero 8°',
# Semillero 9°
'logica_semillero_9': 'Semillero 9°',
'algebra_semillero_9': 'Semillero 9°',
'geometria_semillero_9': 'Semillero 9°',
'conteo_combinatoria_semillero_9': 'Semillero 9°',
'probabilidad_semillero_9': 'Semillero 9°',
# (aritmetica_semillero_9 NO — sin preguntas aún)
# Semillero 10°
'logica_semillero_10': 'Semillero 10°',
'algebra_semillero_10': 'Semillero 10°',
'geometria_semillero_10': 'Semillero 10°',
'conteo_combinatoria_semillero_10': 'Semillero 10°',
'probabilidad_semillero_10': 'Semillero 10°',
'aritmetica_semillero_10': 'Semillero 10°',
# Semillero 11°
'logica_semillero_11': 'Semillero 11°',
'algebra_semillero_11': 'Semillero 11°',
'geometria_semillero_11': 'Semillero 11°',
'conteo_combinatoria_semillero_11': 'Semillero 11°',
'probabilidad_semillero_11': 'Semillero 11°',
'aritmetica_semillero_11': 'Semillero 11°',
```

---

## PARTE 2: UI — Registro (`app.py`)

Cuando el estudiante selecciona nivel **"Semillero de Matemáticas"**:
1. Mostrar selector: **"Grado"** → opciones `6°`, `7°`, `8°`, `9°`, `10°`, `11°`
2. Guardar en campo `grade` del usuario (como string: `'6'`, `'7'`, ..., `'11'`)
3. Si el nivel NO es semillero, `grade = NULL`

---

## PARTE 3: UI — Catálogo de cursos (`app.py`)

**Cambio clave:** Para estudiantes del semillero, el bloque a filtrar NO es simplemente `'Semillero'` sino `'Semillero {grade}°'`.

Donde el sistema determina qué bloque de cursos mostrar al estudiante, agregar esta lógica:

```python
if education_level == 'semillero':
    block = f'Semillero {grade}°'  # ej: 'Semillero 9°'
else:
    # lógica existente para universidad/colegio/concursos
    block = education_level.capitalize()
```

Así, un estudiante de 9° ve SOLO: Lógica Semillero 9°, Álgebra Semillero 9°, Geometría Semillero 9°, Conteo y Combinatoria Semillero 9°, Probabilidad Semillero 9°.

### Nombres legibles en el catálogo
Los nombres de los cursos que se muestran al estudiante deben ser limpios. El `course_name` que genera `sync_items_from_bank_folder()` transforma el filename. Para que se lean bien, los nombres deben resultar en algo como:
- "Lógica Semillero 9°" (no "logica_semillero_9")

Verificar que la función que convierte filename → course name maneje esto correctamente. Si no, agregar un mapeo explícito.

### Encabezado en la sala de estudio
Mostrar: **"🏅 Semillero de Matemáticas — Olimpiadas UdeA — Grado {grade}°"**

---

## PARTE 4: Bancos de preguntas (35 archivos JSON)

Los 35 archivos JSON ya están creados y proporcionados por el usuario. Copiarlos a `items/bank/`.

**Distribución de preguntas por grado:**

| Grado | Preguntas totales | Detalle |
|---|---|---|
| 6° | 32 | Lógica(5), Álgebra(6), Geometría(3), Conteo(5), Probabilidad(2), Aritmética(11) |
| 7° | 14 | Lógica(3), Álgebra(3), Geometría(2), Conteo(3), Probabilidad(2), Aritmética(1) |
| 8° | 15 | Lógica(3), Álgebra(3), Geometría(2), Conteo(4), Probabilidad(2), Aritmética(1) |
| 9° | 12 | Lógica(3), Álgebra(4), Geometría(1), Conteo(2), Probabilidad(2) |
| 10° | 17 | Lógica(4), Álgebra(3), Geometría(4), Conteo(3), Probabilidad(2), Aritmética(1) |
| 11° | 16 | Lógica(2), Álgebra(3), Geometría(4), Conteo(3), Probabilidad(2), Aritmética(2) |

**NOTA:** `aritmetica_semillero_9` no existe (0 preguntas). No crear archivo ni entrada en `_COURSE_BLOCK_MAP` para este caso. Grado 9° tiene 5 materias en lugar de 6.

---

## PARTE 5: Figuras con matplotlib

Crear script `scripts/generate_semillero_figures.py` que genere figuras PNG limpias en `items/images/`.

### Requisitos de cada figura
- Fondo blanco, `plt.axis('off')`, `plt.axis('equal')`
- Líneas negras, grosor 2, labels tamaño 12–14
- Regiones sombreadas en gris `#CCCCCC`
- Ángulos rectos con cuadradito, segmentos iguales con muescas
- PNG, 600×500px aprox, `bbox_inches='tight'`

### Figuras necesarias (14 figuras para ítems del banco)

Generar SOLO las figuras que corresponden a ítems que ya existen en los JSON:

| Figura | Ítem | Descripción geométrica |
|---|---|---|
| `septimo_q14_cuadrados.png` | `gs_7_01` | Dos cuadrados (6cm y 4cm) parcialmente superpuestos |
| `octavo_q14_rectangulos.png` | `gs_8_01` | Rectángulo 20×32 dentro de rectángulo 108×98, marcar centros |
| `octavo_q15_centro_O.png` | `gs_8_02` | Rectángulo con centro O, triángulo OPQ sombreado |
| `noveno_q14_rombo.png` | `gs_9_01` | Rectángulo ABCD (AD=16, AB=12) con rombo AECF inscrito |
| `decimo_q14_paralelogramo.png` | `gs_10_01` | Rectángulo ABCD con P,Q,R,S dividiendo lados en razón 1:2 |
| `decimo_q15_semicirculo.png` | `gs_10_02` | Semicírculo diámetro 5, rectángulo altura 2 inscrito |
| `decimo_q16_cuadrados_circulo.png` | `gs_10_03` | Círculo radio 4, dos cuadrados iguales cubriéndolo |
| `decimo_q20_paralelogramo_ADEF.png` | `gs_10_04` | Triángulo isósceles ABC (AB=AC=28, BC=20) con paralelogramo ADEF |
| `undecimo_q14_paralelogramo.png` | `gs_11_01` | Paralelogramo ABCD, E y F puntos medios, región sombreada |
| `undecimo_q15_equilatero_XYZ.png` | `gs_11_02` | Triángulo equilátero XYZ dividido en tercios, hexágono sombreado |
| `undecimo_q16_triangulo_P.png` | `gs_11_03` | Triángulo rectángulo ABC, punto P interior, áreas 2, 8, 18 |
| `undecimo_q13_tres_cuadrados.png` | `gs_11_04` | Tres cuadrados (lados 9, ?, 4) con vértices A,B,C colineales |
| `primaria_q14_cuadrados.png` | `gs_p_01` (en geometria_semillero_6) | Tres cuadrados I, II, III conectados |
| `decimo_q12_barras.png` | `ps_10_01` (en probabilidad_semillero_10) | Diagrama de barras: notas 1→2, 2→4, 3→7, 4→5, 5→2 |

### Agregar `image_path` a los ítems correspondientes

Después de generar las figuras, editar los JSON para agregar el campo. Ejemplo:

**Antes:**
```json
{"id": "gs_10_02", "content": "Un rectángulo de altura 2...", ...}
```
**Después:**
```json
{"id": "gs_10_02", "content": "Un rectángulo de altura 2...", ..., "image_path": "items/images/decimo_q15_semicirculo.png"}
```

---

## PARTE 6: Rankings (`app.py`)

- Agregar `Semillero` como opción en el filtro de nivel educativo
- **Dentro de Semillero**, agregar sub-filtro por grado (6°–11°)
- Filtrar: `education_level = 'semillero'` AND `grade = <grado_seleccionado>`
- Aplicar en ranking del estudiante Y en panel de ranking del docente

---

## PARTE 7: Seed de prueba (`seed_test_students.py`)

Agregar 2 estudiantes de prueba:

| Usuario | Contraseña | Nivel | Grado | Cursos matriculados |
|---|---|---|---|---|
| `estudiante_semillero_1` | `test1234` | `semillero` | `9` | Todos los cursos de Semillero 9° |
| `estudiante_semillero_2` | `test1234` | `semillero` | `11` | Todos los cursos de Semillero 11° |

Ambos con `is_test_user=1`. Seed idempotente.

---

## PARTE 8: Documentación

Actualizar `CLAUDE.md` y `README.md`:
- Nuevo nivel educativo `semillero` con campo `grade`
- Bloques `Semillero 6°` a `Semillero 11°`
- 35 cursos nuevos en el catálogo
- Tabla de distribución de preguntas por grado

---

## EXCLUIR
- No modificar lógica de ELO, selector adaptativo ni análisis cognitivo
- No cambiar el flujo del admin (excepto que pueda ver el nuevo nivel en filtros)
- No cambiar la estructura de tablas existentes (solo agregar columna `grade`)
- No crear `aritmetica_semillero_9` (no tiene preguntas)
- No eliminar los 6 archivos originales `*_semillero.json` si existieran del prompt anterior — reemplazarlos con los 35 nuevos

---

## Orden de ejecución

1. Leer las 3 skills obligatorias
2. Agregar migración `grade` en ambos repositorios
3. Copiar los 35 JSON a `items/bank/`
4. Agregar 35 entradas en `_COURSE_BLOCK_MAP` de ambos repos
5. Modificar UI de registro (selector de grado condicional)
6. Modificar catálogo para mapear `semillero + grade` → `Semillero {grade}°`
7. Modificar sala de estudio (encabezado con grado)
8. Crear `scripts/generate_semillero_figures.py` → generar 14 PNGs en `items/images/`
9. Actualizar los JSON del banco agregando `image_path` a los 14 ítems con figura
10. Modificar rankings (filtro Semillero + sub-filtro por grado)
11. Actualizar seed de prueba
12. Ejecutar `python scripts/db_sync_check.py`
13. Actualizar CLAUDE.md y README.md

## Criterios de calidad
- Ambos backends funcionan idénticamente
- `db_sync_check.py` pasa sin errores
- Estudiante de grado 9° ve SOLO cursos de Semillero 9° (5 materias)
- Estudiante de grado 6° ve SOLO cursos de Semillero 6° (6 materias)
- Las figuras se renderizan debajo del enunciado
- Rankings de Semillero filtran por grado
- No hay regresiones en universidad/colegio/concursos
