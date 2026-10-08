# Cabos sueltos — qué queda pendiente

Listado rehecho el **2026-08-13**. Todo verificado contra el repo, no de memoria.
Primero lo que falta; el registro de lo cerrado va al final, en una línea por cabo.

**Dónde estamos:** 50 nodos en la ruta, **43 de ellos con la arquitectura de 11 bloques**
(todos los de concepto de Preálgebra N1–N4 y las 16 salas de ALG-N1). Los otros 7 son 4 hubs
y 3 pantallas de N1 con renderer propio. El contenido vive en 44 módulos de
`src/domain/learning/nodes/`; `prealgebra.py` está en 1 727 líneas (arrancó en 4 518) y
`api/routers/student.py` en 1 408 (venía de 1 855).

Verde: **291 tests unitarios · 128 de API · `tsc` limpio · repos en sync · 0 errores de KaTeX.**

---

## 1 · Riesgo real

### ⚠️ A1 — Nada está commiteado

El último commit sigue siendo el de la extracción de Hipertexto. En el working tree:
**13 modificados, 18 borrados, 1 renombrado y 14 sin trackear**, incluidos los dos
directorios que son el corazón del trabajo:

```
?? src/domain/learning/nodes/                      ← los 44 módulos de nodo
?? frontend/src/pages/Student/lessons/blocks/      ← el renderer genérico
```

Es el **único cabo con riesgo de pérdida**. Los demás solo cuestan tiempo.

Los borrados no son nodos: son 9 componentes de frontend (`.tsx` + `.css`) que el renderer
genérico dejó sin uso (Naturals, Integers, Rationals, Irrationals, Reals, Complex,
ClassifierBasic, ClassifierRigorous, Detective). Ningún nodo perdió contenido.

**Falta decidir:** cómo trocear el push «por bloques».

---

## 2 · Esperan una decisión tuya

### A3 — Fundir B01 + B02 en el hub del Nivel 1

Decidido que se funden; **falta decidir si B03** (Escalera de la necesidad) se absorbe ahí o
sigue como nodo aparte.

De esto cuelga un borrado grande: `LevelTwoLesson` (1 034 líneas con su CSS),
`LevelThreeLesson` (931) y `LevelFourLesson` (606) son **2 571 líneas para tres pantallas de
selección con la misma forma** (`welcome_text`, `scene_text`, `icebreaker`, `gating`, lista
de tarjetas, `feedback`). Unificarlas en un renderer de hub común vale la pena, y más ahora
que el hub de Álgebra las convierte en cuatro.

### A3b — Faltan los cierres diagnósticos de N2, N3, N4 y ALG

Solo el Nivel 1 tiene nodo de cierre (`PREALG-N1-B13`). Los otros tres niveles terminan en su
último concepto y no recogen nada: ni conceptos dominados, ni por reforzar, ni recomendación
de siguiente paso. ALG-N1 tampoco lo tiene, aunque su ficha lo describe («recuperar cuatro
acciones: representar → simplificar → repartir → escalar»).

Son **4 nodos de contenido nuevo**. El endpoint `prealgebra-summary` ya existe, pero
`DIAGNOSTIC_NODE_IDS` solo lista los de N1 — a propósito: B13 cierra N1 y resumir el curso
entero desde ahí sería incorrecto. Que el estudiante vea la recomendación de Kemet **depende
de este cabo**.

### C1 — Casi todo el contenido es solo español

**47 de los 50 nodos** llevan el texto hardcodeado en dicts de Python: los 43 de 11 bloques y
los 4 hubs. Solo B01, B02 y B13 son bilingües vía i18n.

La guía unificada exige paridad `es/en` (§19). Decidido hacerla **al terminar las correcciones
y antes del push por bloques**; falta decidir lo de fondo: **si el inglés sigue siendo
objetivo**, porque son 47 nodos de prosa pedagógica, no de etiquetas de interfaz.

### C3 — Datos históricos de Kemet sin validar

Pendientes de revisión experta: la función exacta de Per-Ankh, la descripción de los
harpedonaptas y cualquier razón concreta del canon egipcio.

Riesgo contenido: **en el contenido escrito no se afirma ninguna**. La cuadrícula del taller
es decorado y ningún ejercicio atribuye su proporción a una práctica histórica real.
(De paso: la cuerda de 12 nudos 3-4-5 es un **mito moderno** —Cantor, 1882— sin fuente
antigua, y tampoco aparece en el contenido.)

**Falta decidir:** quién valida.

### D4 — Los ítems de Hipertexto no alimentan los nodos ni el banco

Era el propósito de la extracción. **4 656 ítems** en `items/source/` (3 132 Hipertexto,
1 464 Caminos, 60 EPA8), ninguno en uso: la práctica de los 43 nodos está escrita a mano y
`items/bank/` no los tiene.

El hueco **no es de formato**. Medido el 2026-08-13:

| Campo del banco | Qué hay en la extracción |
|---|---|
| `content` | `enunciado` ✓ |
| `difficulty` | `dificultad` ✓ — ya viene en escala ELO (400–1900) |
| `topic` | `seccion` + `unidad` + `conjunto` (N/Z/Q/R/I) — derivable |
| `correct_option` | `respuesta` ✓ |
| **`options`** | **no existe** |

De los **1 850** ítems marcados `practica_seleccion` o `practica_numerica`, los que traen
opciones escritas son **60** (todos de EPA8). La etiqueta significa «**convertible** a opción
múltiple» —algunos ítems lo dicen en su `nota`—, no «ya lo es».

La extracción aportó lo caro de un ítem —enunciado, contexto, respuesta correcta y dificultad
calibrada— y falta lo que ningún libro trae: **los distractores**. Y un distractor bueno no es
un número al azar, es el resultado de cometer un error concreto.

Si se decide hacerlo, el trabajo se reparte así:

- **168** con respuesta numérica limpia — donde un distractor mecánico es al menos discutible.
- **1 403** con respuesta corta (<40 caracteres).
- **279** con respuesta larga o explicada — no son de opción múltiple; su sitio es
  `procedimiento_abierto`.

**Práctica de los nodos** es aparte y más caro: además de distractores pide escalera
`n1/n2/n3` y feedback por distractor, cada uno atado a un error focal.

Hueco conocido aparte: **1 385 ítems `simbolico`** sin respuesta tecleable única. `text_exact`
cubre monomios y sumas cortas, no expresiones con paréntesis.

**Falta decidir:** si se escriben distractores, y para cuántos de los 1 850.

---

## 3 · Aplazados a propósito

### A4 y A5 — El arte

**Decisión del 2026-08-13: los prompts no se corren por ahora.** No es trabajo pendiente, es
una espera. Los prompts están escritos y autocontenidos:

| | Prompts | Destino | Estado del arte |
|---|---|---|---|
| **N2 · la ciudad** | 22, en `n2-ciudad-edificios.md` | `frontend/public/leccion/02-prealg-n2-mercado/` | Los 22 PNG actuales siguen dibujando **puestos de mercado**, que es lo que se descartó |
| **ALG-N1 · Kemet** | 36, en `alg-n1-kemet-PROMPTS.md` (hub + 17 obligatorias + 16 trampas) | `frontend/public/leccion/05-alg-n1-kemet/` | No existe |

Cuando lleguen los PNG de Kemet hay que añadir `katia.image` a cada módulo; el documento trae
el snippet.

**Efecto secundario mientras dure:** el hub de Kemet declara
`/leccion/05-alg-n1-kemet/a00-hub-papiro-katia.png`, que no existe → **404 en cada carga
del hub**. Es el único asset roto conocido. Si el aplazamiento es largo, conviene quitarle esa
línea al hub y devolverla con el PNG.

---

## 4 · Esperan un insumo que no está en el repo

### C2 — Citas: emparejadas, falta anclarlas

Ninguna se elimina. Viven en `Fase_2/CITAS_EN_REMOJO.md`, y la regla mientras tanto es: **se
pueden usar para diseñar contenido, no para respaldarlo por escrito.**

- **Las siete de N2** — el par afirmación↔cita **sí estaba escrito**, no en el checklist sino
  en la sección de referencias de cada `F2_nodo_*.md`. Recuperado y tabulado: las siete
  atribuciones son correctas. Una corrección de año: los modos de representación son
  **Bruner (1966)**, no 1960 (ese es *The Process of Education*).
- **`invierte_cociente`** — tiene respaldo: **Fischbein, Deri, Nello & Marino (1985)**
  documenta el modelo implícito de la división partitiva y su restricción tácita de que el
  divisor sea menor que el dividendo (623 estudiantes, grados 5/7/9), con replicación en
  Maffia et al. (2022).
- **La dosis del intento genuino** — no necesita fuente: está declarada como predicción para
  el piloto. Se resuelve con datos.

**Falta el insumo:** la lista de la **biblioteca aprobada** del proyecto. Sin ella, «anclar»
no tiene destino. Sweller y Hattie & Timperley ya se citan en la spec de B06 y en las siete
fichas de Fase 1, así que probablemente ya estén dentro.

### C5 — Los tres huecos de cada spec

Las 43 specs se generan con `scripts/generar_specs.py` → `Implementacion/specs/generadas/`,
~400 líneas cada una. Ya se puede revisar la pedagogía sin leer Python.

Tres secciones **no salen del código** y quedan marcadas `PENDIENTE` en cada archivo:

| Hueco | Qué va ahí |
|---|---|
| A0 | Estándares DBA / ICFES / grado y tiempo estimado |
| A13 | Citas (depende de C2) |
| A14 | Notas de handoff a Design |

Se escriben a mano una vez. Al rellenar un archivo hay que **sacarlo de `generadas/`**:
regenerar pisa la carpeta entera. B06 sigue siendo la única spec completa a mano (1 082
líneas) y es el modelo de qué va en esos tres huecos.

### D1 — Accesibilidad: falta la parte que no se lee en el código

El código está corregido (ver §5). Queda lo que necesita a alguien delante de la pantalla:
**revisión con lector de pantalla real** (NVDA / VoiceOver) y **medición de contraste**.

### D2 — Calibración del piloto

Revisión rápida hecha. Falta la calibración con **datos de uso real**, que solo llega con el
piloto. Los 7 ítems de práctica por nodo siguen siendo una convención, no una medida.

---

## 5 · Cerrado

| Cabo | Fecha | Qué quedó |
|---|---|---|
| **A2** ALG-N1 no salía en el mapa | 2026-08-05 | Encadenado tras el MCM, con test |
| **A6** Expansión de ALG-N1 | 2026-08-12 | De 4 nodos colapsados a **17**: hub + 4 casas × 4 salas, 16 errores focales distintos entre sí y de los 27 de Preálgebra |
| **B1** El molde viejo | 2026-08-05 | −2 500 líneas entre `prealgebra.py`, `es.ts` y `en.ts`. Sobrevive `mapTitle` |
| **B3** Rama muerta `text_exact` | 2026-08-05 | Conectada: un ítem puede pedir que se **teclee** la expresión. Los paréntesis se rechazan en vez de borrarse |
| **B4** `course_map` no escalaba | 2026-08-12 | El mapa se **deriva** de `unlock_after` vía `curriculum_map_rows`. `student.py`: 1 855 → 1 408 líneas |
| **C4** La ruta de repaso no cubría Álgebra | 2026-08-12 | Era peor: 40/43 focales y 331/356 tags sin ruta. Ahora sale de `NODE_MODULES`: **0 sin ruta**, con test |
| **C5** Specs | 2026-08-13 | 43 generadas desde los módulos (quedan los 3 huecos de §4) |
| **D1** Accesibilidad (código) | 2026-08-13 | `role="img"` en las fórmulas con lectura, `.sr-only`, símbolo además de color, y las dos zonas de subida operables con teclado |
| **D3** ¿Álgebra mueve ELO? | 2026-08-13 | **No.** Los 50 nodos van `affects_elo: False`, y el endpoint de interacciones no toca el motor |

---

## Orden que sugiero

1. **A1 — commitear.** Es lo único que puede perderse.
2. **A3** — la decisión sobre B03 desbloquea ~2 500 líneas de borrado.
3. **C1** — si el inglés se cae del alcance, deja de ser deuda y pasa a ser una línea en la guía.
4. **A3b** — 4 nodos, y sin ellos la ruta de repaso no llega al estudiante fuera de N1.
5. **D4** — el más grande; conviene decidirlo con la vista puesta en el piloto.
