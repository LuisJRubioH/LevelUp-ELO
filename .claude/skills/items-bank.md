---
name: items-bank
description: >
  Guía para trabajar con el banco de preguntas de LevelUp-ELO. Usar SIEMPRE
  que la tarea involucre: crear preguntas nuevas, editar ítems existentes,
  agregar cursos al banco, validar formato JSON, depurar JSONDecodeError en
  items/bank/, agregar imágenes a preguntas, o verificar que correct_option
  coincida con options. Incluye plantillas listas para copiar y checklist
  de validación.
---

# Skill: items-bank

## Ubicación y estructura

```
items/bank/
├── algebra_lineal.json
├── calculo_diferencial.json
├── calculo_integral.json
├── calculo_varias_variables.json
├── ecuaciones_diferenciales.json
├── probabilidad.json
├── algebra_basica.json
├── aritmetica_basica.json
├── trigonometria.json
├── geometria.json
├── DIAN.json
└── SENA.json
```

Cada archivo = un curso. El nombre del archivo (sin `.json`) es el `course_id` que el sistema usa internamente.

---

## Formato de un ítem

### Campos requeridos

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | string | Único en **todo el banco** (no solo en el archivo). Convención: `{prefijo_curso}_{número}` |
| `content` | string | Enunciado de la pregunta. LaTeX con `$...$` inline |
| `difficulty` | int | Rating ELO inicial. Rango recomendado: 600–1800 |
| `topic` | string | Tema dentro del curso. Ej: `"Derivadas"`, `"Integrales"` |
| `options` | array de strings | 2 a 4 opciones. Soportan LaTeX |
| `correct_option` | string | Debe coincidir **carácter por carácter** con uno de `options` |

### Campos opcionales

| Campo | Tipo | Notas |
|---|---|---|
| `image_url` | string | URL directa a imagen. Tiene prioridad sobre `image_path` |
| `image_path` | string | Ruta relativa al repo. Ej: `"items/images/figura.png"` |

---

## Plantillas

### Pregunta sin imagen

```json
{
    "id": "cd_01",
    "content": "¿Cuál es la derivada de $\\sin(x)$?",
    "difficulty": 650,
    "topic": "Derivadas básicas",
    "options": [
        "$\\cos(x)$",
        "$-\\cos(x)$",
        "$\\sin(x)$",
        "$-\\sin(x)$"
    ],
    "correct_option": "$\\cos(x)$"
}
```

### Pregunta con imagen (URL externa)

```json
{
    "id": "geo_01",
    "content": "Calcula el área sombreada de la figura.",
    "difficulty": 1200,
    "topic": "Áreas",
    "options": [
        "$12\\pi$ cm²",
        "$8\\pi$ cm²",
        "$16\\pi$ cm²",
        "$4\\pi$ cm²"
    ],
    "correct_option": "$12\\pi$ cm²",
    "image_url": "https://raw.githubusercontent.com/usuario/repo/main/items/images/area_01.png"
}
```

### Pregunta con imagen (ruta local)

```json
{
    "id": "tri_05",
    "content": "¿Cuál es el valor de $\\alpha$?",
    "difficulty": 900,
    "topic": "Trigonometría",
    "options": ["$30°$", "$45°$", "$60°$", "$90°$"],
    "correct_option": "$45°$",
    "image_path": "items/images/triangulo_alpha.png"
}
```

---

## Reglas de LaTeX en JSON

**La causa más común de `JSONDecodeError` son los backslashes sin escapar.**

En JSON, `\` es un carácter especial de escape. Para escribir un backslash literal, se necesitan dos: `\\`.

### Tabla de conversión

| Lo que quieres escribir | Cómo escribirlo en JSON |
|---|---|
| `\frac{a}{b}` | `\\frac{a}{b}` |
| `\sin(x)` | `\\sin(x)` |
| `\cos(x)` | `\\cos(x)` |
| `\alpha` | `\\alpha` |
| `\beta` | `\\beta` |
| `\sqrt{x}` | `\\sqrt{x}` |
| `\int_0^1` | `\\int_0^1` |
| `\sum_{i=1}^n` | `\\sum_{i=1}^n` |
| `\vec{v}` | `\\vec{v}` |
| `\begin{pmatrix}` | `\\begin{pmatrix}` |

### Ejemplo completo

```json
"content": "Si $f(x) = \\frac{x^2 + 1}{\\sqrt{x}}$, ¿cuál es $f'(x)$?",
"options": [
    "$\\frac{3x^2 - 1}{2x^{3/2}}$",
    "$\\frac{2x\\sqrt{x} - 1}{2x}$",
    "$\\frac{x^2 - 1}{2\\sqrt{x^3}}$",
    "$\\frac{3\\sqrt{x}}{2}$"
]
```

---

## Regla crítica: `correct_option` debe coincidir exactamente

El sistema compara `correct_option` con las opciones usando igualdad de strings. Un espacio de más, un signo diferente, o una mayúscula incorrecta hacen que la pregunta siempre marque como incorrecta.

### Checklist de coincidencia

Antes de guardar un ítem, verificar:

- [ ] `correct_option` está escrito idéntico a uno de los elementos de `options`
- [ ] Mismos espacios (incluyendo espacios antes/después del `$`)
- [ ] Mismo uso de mayúsculas
- [ ] Mismo LaTeX (ej. `$\\frac{1}{2}$` ≠ `$\\frac{1}{2} $`)

### Ejemplo de error común

```json
"options": ["$\\cos(x)$", "$-\\cos(x)$", "$\\sin(x)$"],
"correct_option": "$cos(x)$"   ← INCORRECTO: falta el backslash
```

```json
"options": ["$\\cos(x)$", "$-\\cos(x)$", "$\\sin(x)$"],
"correct_option": "$\\cos(x)$"   ← CORRECTO
```

---

## IDs únicos: convención y verificación

### Convención de prefijos por curso

| Curso | Prefijo sugerido |
|---|---|
| Álgebra Lineal | `al_` |
| Cálculo Diferencial | `cd_` |
| Cálculo Integral | `ci_` |
| Cálculo Varias Variables | `cvv_` |
| Ecuaciones Diferenciales | `ed_` |
| Probabilidad | `prob_` |
| Álgebra Básica | `ab_` |
| Aritmética Básica | `arit_` |
| Trigonometría | `tri_` |
| Geometría | `geo_` |
| DIAN | `dian_` |
| SENA | `sena_` |

### Verificar unicidad antes de agregar

```bash
# Buscar si un ID ya existe en todo el banco
grep -r '"id": "cd_01"' items/bank/
```

Si el grep devuelve resultados, el ID ya está en uso — cambiar el número.

---

## Dificultad: escala de referencia

| Rango | Nivel aproximado |
|---|---|
| 600–800 | Conceptos básicos, definiciones directas |
| 800–1000 | Aplicación directa de fórmulas |
| 1000–1200 | Problemas de uno o dos pasos |
| 1200–1400 | Problemas con múltiples conceptos |
| 1400–1600 | Problemas complejos, análisis requerido |
| 1600–1800 | Nivel avanzado, concursos o postgrado |

El sistema ajusta automáticamente la dificultad con el tiempo basado en las respuestas. El valor inicial es solo un punto de partida.

---

## Imágenes: recomendaciones

- **Formatos**: PNG, JPG, SVG, GIF, WebP.
- **Ancho recomendado**: 400–1200 px. La imagen se ajusta al contenedor automáticamente.
- **Fondo**: blanco o transparente (PNG) para buena legibilidad.
- **Resolución mínima**: 150 DPI si contiene texto o fórmulas.
- La imagen es siempre opcional — si la URL no carga o no existe el campo, la pregunta funciona con solo texto.
- Si ambos `image_url` e `image_path` están presentes, `image_url` tiene prioridad.

---

## Agregar un curso nuevo: proceso completo

1. **Crear el archivo JSON:**
   ```
   items/bank/mi_curso.json
   ```
   El archivo debe ser un array JSON válido de ítems:
   ```json
   [
       {
           "id": "mc_01",
           "content": "Enunciado...",
           ...
       },
       ...
   ]
   ```

2. **Registrar en ambos repositorios** (ver skill `db-dual-backend.md`):
   ```python
   # En _COURSE_BLOCK_MAP de sqlite_repository.py Y postgres_repository.py
   'mi_curso': 'Universidad',  # o 'Colegio' o 'Concursos'
   ```

3. **Reiniciar la app** — `sync_items_from_bank_folder()` registra automáticamente los ítems sin sobrescribir ratings existentes.

---

## Depurar JSONDecodeError

Si el sistema lanza `JSONDecodeError` al arrancar, es casi siempre por LaTeX mal escapado.

```bash
# Validar todos los archivos del banco
python -c "
import json, os
for f in os.listdir('items/bank'):
    if f.endswith('.json'):
        try:
            json.load(open(f'items/bank/{f}'))
            print(f'OK: {f}')
        except json.JSONDecodeError as e:
            print(f'ERROR en {f}: {e}')
"
```

### Errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| `Invalid \\escape` | Backslash LaTeX sin doblar | `\frac` → `\\frac` |
| `Expecting value` | Coma trailing o array vacío | Revisar última llave/corchete |
| `Unterminated string` | Comilla sin cerrar en `content` u `options` | Revisar strings con LaTeX complejo |
| `correct_option not in options` (runtime) | Mismatch de strings | Copiar/pegar la opción exacta desde `options` |

---

## Validación rápida antes de guardar

```python
import json

def validar_item(item):
    requeridos = ['id', 'content', 'difficulty', 'topic', 'options', 'correct_option']
    for campo in requeridos:
        assert campo in item, f"Falta campo: {campo}"
    
    assert isinstance(item['difficulty'], (int, float)), "difficulty debe ser número"
    assert 600 <= item['difficulty'] <= 1800, "difficulty fuera del rango recomendado"
    assert len(item['options']) >= 2, "Mínimo 2 opciones"
    assert item['correct_option'] in item['options'], \
        f"correct_option '{item['correct_option']}' no está en options"
    print(f"✓ {item['id']} válido")

# Uso
with open('items/bank/mi_curso.json') as f:
    items = json.load(f)
for item in items:
    validar_item(item)
```
