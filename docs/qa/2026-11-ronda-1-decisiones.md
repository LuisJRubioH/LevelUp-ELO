# QA ronda 1 — decisiones y enmienda

Acompaña a [`2026-11-ronda-1.md`](2026-11-ronda-1.md). Cada punto trae la evidencia, la
recomendación con sus consecuencias y lo que cambia.

**Estado: D1 a D5 aprobadas por la owner el 2026-11-12, con la opción recomendada en cada una.**
Nada está implementado todavía. D1 y D2 quedaron escritas en spec 003 como entrega L6, en la rama
`003-learning-path-l6` (spec, lista de calidad, `plan-l6.md` y `tasks-l6.md`); ese es ahora el
texto vigente, y el borrador de más abajo se conserva solo como registro de lo que se propuso.

| # | Decisión | Recomendación | Vía si se aprueba |
|---|---|---|---|
| D1 | Q2: qué responde la lección cuando el estudiante marca solo parte de las opciones correctas | Decirle la verdad: «lo que marcaste es correcto, falta al menos una» | Enmienda de spec 003, entrega **L6** |
| D2 | Q4: qué es un paso «Complétalo tú» | Pensar y revelar: el paso se oculta tras un botón, sin campo ni registro | Enmienda de spec 003, entrega **L6** |
| D3 | Q3: el mensaje por defecto de B03–B12 | Diez mensajes propios, uno por nodo, como ya tienen los otros 42 | Contenido, sin spec |
| D4 | Q6: grado para Colegio en el registro | No cambiar: es una regla ya decidida | Ninguna; se cierra |
| D5 | Q12: textos que citan códigos internos («B05», «N4-C04») | Nombrar el nodo como lo ve el estudiante, con una guarda | Contenido, sin spec |

---

## D1 — Q2: una respuesta parcial no es una respuesta equivocada

**Evidencia.** La pregunta de abstracción es de varias respuestas en los 52 nodos: 43 tienen dos
opciones correctas de cuatro y 9 tienen una de tres. El servidor solo da por buena la selección
completa (`src/domain/learning/prealgebra.py`, rama `multi_select` de `evaluate_interaction`) y,
como la pregunta se registra sin mensajes propios (`prealgebra.py:1979-1992`), todo lo demás
recibe el `feedback.default` del nodo. El tester marcó una opción correcta en B04 y leyó «Todavía
no. Revisa el procedimiento paso a paso y vuelve a intentarlo.»: concluyó que la opción correcta
estaba mal. El motor ya distingue los tres casos (`feedback_missing`, `feedback_trap`,
`feedback_incorrect`); solo falta darles un mensaje.

**Opciones.**

- **(a) Tres mensajes, iguales en todos los nodos — recomendada.**
  - Solo opciones correctas, pero no todas: «Vas bien: lo que marcaste es correcto, pero falta al
    menos una opción más.»
  - Alguna opción incorrecta marcada: «Al menos una de las que marcaste no aplica. Revisa cada
    opción contra los casos de arriba.»
  - Todas las correctas: el mensaje de acierto de hoy.
- (b) Dejar solo el aviso «puede haber más de una respuesta correcta» (ya está en el PR 182). El
  estudiante sabe que puede haber varias, pero un acierto parcial se sigue leyendo como error.
- (c) Aceptar como buena cualquier opción correcta. Descartada: la pregunta existe para que el
  estudiante vea *todo* el patrón, y habría que redefinir qué guarda el historial del docente.

**Consecuencias de (a).**

- No revela la clave: nunca nombra una opción. Sí confirma que las marcadas son correctas, lo
  que es aceptable porque la pregunta no bloquea el cierre del nodo (spec 003 N9) y no mueve
  ningún rating (FR-001).
- El historial del docente no cambia: la respuesta parcial se guarda como «no acertada»
  (FR-040, N11). El mensaje cambia; el registro no.
- Vale también para cualquier pregunta de varias respuestas de la práctica que no defina su
  propio mensaje de «falta una».

**Además, sin spec (diseño visual):** dar a las opciones de una pregunta de varias respuestas una
casilla visible (☐/☑). Hoy la opción marcada apenas cambia el borde y un segundo toque la desmarca
sin que se note, que es lo que le pasó al tester en B03.

## D2 — Q4: «Complétalo tú» sin nada que completar

**Evidencia.** `FADED_STEPS` (`ElevenBlockLesson.tsx:57`) oculta los últimos 2 pasos de cada
ejemplo resuelto en la presentación «intermedio» y los últimos 3 en «avanzado». El paso oculto
muestra el texto «Complétalo tú» y nada más (`LessonBlocks.tsx:475-478`): no hay campo, no hay
forma de verlo, y la solución aparece debajo de todos modos. Los 104 ejemplos resueltos tienen 5
pasos. Hay un daño adicional que el tester no llegó a ver: la pregunta de autoexplicación cuelga
de un paso concreto, y ese paso queda oculto en 9 ejemplos (intermedio) y en 29 (avanzado). Ahí
la lección pide «explica este paso» sobre un paso que no se puede leer. Ninguna spec ni regla de
AGENTS describe hoy qué hace la presentación con los ejemplos.

**Opciones.**

- **(a) Pensar y revelar — recomendada.** El paso oculto muestra «Tu turno: piensa este paso
  antes de verlo» y un botón «Comparar con el paso». Al tocarlo aparece el paso (y su
  autoexplicación, si la lleva). La solución del ejemplo aparece cuando todos los pasos están a la
  vista. No hay campo y no se envía ni se guarda nada.
- (b) Un campo con respuesta calificada. Descartada: los pasos son prosa («¿Es entero? No: cae
  entre −1 y 0…»), no se pueden calificar por coincidencia; pedirían claves nuevas para más de
  300 pasos, y el texto libre de un menor no se puede guardar (FR-006).
- (c) Quitar el desvanecimiento. Descartada salvo que se prefiera no diferenciar por nivel: es lo
  único que hoy distingue «intermedio» y «avanzado» de «básico» en un ejemplo resuelto.

**Consecuencias de (a).** Solo cambia el frontend (`WorkedExample`). No toca contenido, base de
datos ni rating. Conserva la idea pedagógica del ejemplo desvanecido —el estudiante intenta el
paso antes de verlo— sin exigir calificarlo. La comprobación `faded-no-input` del barrido pasa a
exigir el botón, y hoy salta en los 52 nodos.

## D3 — Q3: el mensaje por defecto de B03–B12

**Corrección al triage.** El síntoma que reportó el tester (el mensaje en la pregunta de
abstracción) queda resuelto por D1. Lo que resta es otra cosa y es contenido, fuera del alcance
de spec 003 (§ Out of Scope: «Content authoring»): en 42 nodos el `feedback.default` es una
estrategia de comprobación propia del nodo («Comprueba elevando al cuadrado: si no vuelves al
radicando, algo falló»), y en los 10 nodos de Preálgebra N1 (B03–B12) es el genérico «Revisa el
procedimiento paso a paso y vuelve a intentarlo.». Ese mensaje lo lee el estudiante en cada
respuesta numérica equivocada de la práctica, del puente y del cierre: entre 5 y 8 preguntas por
nodo.

**Recomendación:** seguir el patrón de los otros 42. Textos propuestos, para corregir o aprobar:

| Nodo | `feedback.default` propuesto |
|---|---|
| B03 escalera | Sube la escalera peldaño por peldaño: pregunta en cada conjunto si el número cabe y cuenta los «sí». |
| B04 naturales | Vuelve a contar: ¿qué se junta, qué se repite y qué montón está vacío? El vacío también cuenta: vale 0. |
| B05 enteros | Decide primero el signo —¿debes o tienes?, ¿sube o baja?— y después haz la cuenta. |
| B06 racionales | Escribe la división como fracción y comprueba al revés: el resultado por el divisor debe devolverte el dividendo. |
| B07 irracionales | Resuelve cada raíz y mira cada decimal antes de decidir: si la raíz es exacta o el decimal se repite, es racional. |
| B08 reales | Ubícalo en la recta: ¿entre qué dos números queda? Para hallar uno en medio, promedia los extremos. |
| B09 complejos | Separa las dos partes: la real va sola y la imaginaria es el número que acompaña a $i$. Recuerda que $i^2=-1$. |
| B10 clasificador básico | Resuelve primero la división o la raíz y clasifica el resultado, no la forma en que venía escrito. |
| B11 clasificador riguroso | Pasa el número por los cinco conjuntos, uno por uno: puede estar en varios a la vez, pero nunca en $\mathbb{Q}$ y en $\mathbb{I}$ juntos. |
| B12 detective | Lee la frase en el orden en que está escrita y busca un contraejemplo: con uno solo, la frase es falsa. |

Si se aprueba: una línea en AGENTS V2-R11 («el `feedback.default` de un nodo es su estrategia de
comprobación; nunca un mensaje genérico») y una prueba que falle si dos nodos comparten el mismo
`default`.

## D4 — Q6: el grado en el registro de Colegio

**Corrección al triage.** El registro lo dejó como decisión abierta. No lo es: es una regla ya
decidida y probada. Spec 004 FR-040 y `src/domain/identity.py::student_level_problem` dicen que
el grado solo aplica a Semillero («para este nivel elige "No aplica"»), tanto en el registro
público como cuando el admin crea la cuenta. El grado de un estudiante de colegio vive en su
grupo (`groups.grade`, spec 009), y ningún curso de Colegio se filtra por grado.

**Recomendación: cerrar Q6 como «por diseño».** Reabrirlo sería contradecir una decisión
registrada, y solo la owner puede hacerlo. No lo recomiendo: pedir el grado a un menor no
cambiaría nada de lo que ve, y sería un dato más que guardar sin uso.

## D5 — Q12 (nuevo): códigos internos en los textos

**Evidencia.** La captura de B04 del tester dice «Ese único agujero es el que abre B05». El
estudiante nunca ve «B05»: el mapa lo llama «Enteros». Hay 80 textos así en 25 nodos («eso abre
B06», «lo verás en N4-C04», «viene de B05»), sobre todo en las notas del cierre (32) y en las
definiciones (13).

**Recomendación:** nombrar el nodo como lo nombra el mapa («el peldaño de los enteros», «cuando
llegues a Factorización prima») y agregar una guarda que falle si un texto visible cita un código
de nodo. Es contenido: sin spec, un PR aparte, trabajo para Sonnet con la tabla código → nombre.

---

## Borrador de la enmienda a spec 003 — entrega L6 (para D1 y D2)

**Sustituido por la rama `003-learning-path-l6`.** Al aplicarlo cambiaron tres cosas: FR-062
también fija la etiqueta de error de cada selección; hay un escenario más (US7-AS4: una pregunta
con mensajes propios los conserva); y el segundo mensaje quedó neutro («Al menos una de las
opciones que marcaste no es correcta. Revísalas una por una.») para que también se lea bien en
una pregunta de práctica, que no tiene «casos de arriba».

**§ Deliveries — fila nueva**

```markdown
| **L6** | Feedback that tells a partial answer from a wrong one, and worked-example steps the student thinks through before seeing them (QA round 1: Q2, Q4) | planned |
```

**§ User Scenarios — dos historias nuevas**

```markdown
### User Story 7 - The lesson tells me the truth about my answer (Priority: P2) — L6

**Why this priority**: a student who marked one of the two right options of an abstraction
question read «todavía no… vuelve a intentarlo» and concluded the right option was wrong
(`docs/qa/2026-11-ronda-1.md`, Q2).

**Acceptance Scenarios**:

1. **US7-AS1** — **Given** a multiple-answer question with two right options and no feedback of
   its own, **When** the student sends one of them and no other option, **Then** the feedback says
   that what they marked is right and that at least one more is missing, and names no option.
2. **US7-AS2** — **Given** the same question, **When** the student sends a selection that holds an
   option that is not right, **Then** the feedback says that at least one marked option does not
   hold, and names no option.
3. **US7-AS3** — **Given** either answer, **When** it is stored, **Then** it is stored as not
   right, as today.

### User Story 8 - I think a step through before I see it (Priority: P2) — L6

**Why this priority**: in the «intermedio» and «avanzado» presentations a worked example replaces
its last steps with «Complétalo tú» and offers nothing to complete, and it asks the student to
explain a step they cannot read (`docs/qa/2026-11-ronda-1.md`, Q4).

**Acceptance Scenarios**:

1. **US8-AS1** — **Given** a student whose presentation withholds steps, **When** they open a
   worked example, **Then** each withheld step shows an invitation to think it through and a
   control that reveals it.
2. **US8-AS2** — **Given** a withheld step, **When** the student reveals it, **Then** the step is
   shown, with its self-explanation prompt if it carries one — and not before.
3. **US8-AS3** — **Given** a withheld step not yet revealed, **When** the example is on screen,
   **Then** its solution is not shown.
4. **US8-AS4** — **Given** a withheld step, **When** the student reveals it, **Then** nothing is
   sent to the server.
5. **US8-AS5** — **Given** a student in the «básico» presentation, **When** they open a worked
   example, **Then** no step is withheld.
```

**§ Requirements — bloque nuevo**

```markdown
**Honest feedback and withheld steps (L6)**

- **FR-060** [CHANGE]: When a student answers a multiple-answer interaction that defines no
  feedback of its own with right options only, but not all of them, the system shall answer that
  the marked options are right and at least one is missing. *(Today it answers with the node's
  default message, the one a wrong answer gets.)*
- **FR-061** [CHANGE]: When that answer holds an option that is not right, the system shall answer
  that at least one marked option does not hold. Neither answer shall name an option.
- **FR-062** [AS-IS]: The system shall store an incomplete multiple-answer selection as not right.
- **FR-063** [AS-IS]: The system shall withhold no step of a worked example in the «básico»
  presentation, its last two in «intermedio» and its last three in «avanzado».
- **FR-064** [CHANGE]: Where a step of a worked example is withheld, the system shall show it only
  after the student asks for it, shall show a self-explanation prompt only with the step it
  belongs to, and shall show the example's solution only once every step is shown. *(Today a
  withheld step reads «Complétalo tú» and can never be seen; the prompt and the solution show
  regardless.)*
- **FR-065** [AS-IS]: The system shall send nothing to the server when a step is revealed.
```

**§ New Decisions and Contradictions — filas nuevas** (la owner sella la aprobación)

```markdown
| N12 | A multiple-answer selection that is right but incomplete gets the feedback of a wrong one (QA Q2). | **Recommended**: FR-060, FR-061 — two messages shared by every node; storage unchanged (FR-062). |
| N13 | A withheld worked-example step offers nothing to complete, and nothing specifies the presentation's effect on worked examples (QA Q4). | **Recommended**: think, then reveal (FR-064); no field, nothing stored. The band cut-offs stay provisional and outside this delivery. |
```

**§ Traceability — filas nuevas, `PENDING` mientras L6 esté abierta**

```markdown
| US7-AS1 | L6 | `PENDING` |
| US7-AS2 | L6 | `PENDING` |
| US7-AS3 | L6 | `PENDING` |
| US8-AS1 | L6 | `PENDING` |
| US8-AS2 | L6 | `PENDING` |
| US8-AS3 | L6 | `PENDING` |
| US8-AS4 | L6 | `PENDING` |
| US8-AS5 | L6 | `PENDING` |
| FR-060 | L6 | `PENDING` |
| FR-061 | L6 | `PENDING` |
| FR-062 | L6 | `PENDING` |
| FR-063 | L6 | `PENDING` |
| FR-064 | L6 | `PENDING` |
| FR-065 | L6 | `PENDING` |
```

## Tareas de implementación (borrador; las vigentes están en `tasks-l6.md`)

Orden que exige el proceso: primero las pruebas de lo que no cambia, que pasan sobre el código
de hoy; después cada prueba de un cambio, que falla antes de su implementación.

1. **Pins `[AS-IS]`** (pasan sin tocar código):
   - FR-062: `tests/unit/domain/` — una selección parcial de `…-ABSTRACCION` devuelve
     `is_expected == False`.
   - FR-063, FR-065: `frontend/e2e/` — en «básico» no hay paso oculto; en «intermedio» son los dos
     últimos; revelar un paso no dispara ninguna petición.
2. **FR-060, FR-061** (`src/domain/learning/prealgebra.py`): la pregunta de abstracción y todo
   `multi_select` sin mensajes propios responden con dos claves nuevas compartidas; el texto de
   esas claves vive en un solo lugar, no en 52 nodos. **Corrección (2026-11-12):** aquí decía que
   había que comprobar primero la opción de más. Es un error: reordenar el motor cambiaría la
   etiqueta de error guardada en 3 969 de las 5 412 selecciones posibles. La calificación y la
   etiqueta no se tocan; solo se elige aparte el mensaje (`plan-l6.md` § Design). Pruebas en `tests/unit/domain/` y un caso en
   `frontend/e2e/spec003-l2-lesson.spec.ts`, que ya cubre el reintento de la abstracción.
3. **FR-064** (`WorkedExample`, `LessonBlocks.tsx`): pensar y revelar; la autoexplicación y la
   solución esperan a su paso. Pruebas en `frontend/e2e/`.
4. **Barrido:** `faded-no-input` exige el control de revelar (`scripts/qa/lib.js`).
5. **Cierre de L6:** llenar las 14 filas de trazabilidad y marcar la entrega `closed`.

Aparte, sin spec: D3 (diez textos, la línea de V2-R11 y su prueba), D5 (80 textos y su guarda) y
la casilla visible de D1.
