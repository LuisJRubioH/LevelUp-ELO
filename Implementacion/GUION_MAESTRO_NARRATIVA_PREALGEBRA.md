# Guión maestro — narrativa, lógica de ejemplos y representación gráfica (Preálgebra N1–N4)

Documento único de consulta para escribir niveles nuevos (N5+) sin releer los 8 archivos
donde hoy vive esta información repartida. No sustituye a las fuentes — si algo no cuadra,
la fuente manda:

- `CLAUDE.md` reglas `V2-R11`–`V2-R14` (fuente de verdad legal del formato por nivel)
- `.claude/skills/prealgebra-node-author/SKILL.md` (estructura de dict/contenido)
- `.claude/skills/prealgebra-narrative-style/SKILL.md` (presentación visual + mundos)
- `Implementacion/FORMATO_nodo_conjuntos_numericos.md` (N1 detallado)
- `Implementacion/PROMPT_N2_extension_conjuntos.md` (N2 detallado, tablas de cierre)
- `Implementacion/PROMPT_N4_divisibilidad.md` (N4 detallado)
- `Implementacion/image-prompts/n{1..4}-*.md` (prompts de imagen ya escritos, por nodo)

Este documento es la síntesis. Antes de escribir un nodo/nivel nuevo: leer esto entero una
vez, luego ir al nodo de referencia del nivel más parecido y copiar su dict real.

---

## 1. Los 4 mundos — uno por nivel, vocabulario sin cruces

Un mismo universo (Grecia clásica + KatIA cyborg), pero cada nivel grande vive en un espacio
físico propio. El vocabulario de un espacio **nunca** aparece en otro nivel — regla nacida de
una auditoría (2026-07) que encontró "ágora" filtrada en 5/6 nodos de N2 y 4/5 de N3.

| Nivel | Espacio | Vocabulario propio | Toque retrofuturista |
|---|---|---|---|
| N1 — Conjuntos numéricos | **El ágora** | columnas, mármol, tablillas, plaza pública, ciudadanos, escalinatas | ninguno forzado — KatIA es la única nota tech |
| N2 — Operaciones básicas | **El mercado** | puestos, mercaderes, telas, cerámica, especias, cestas, balanzas de mano | ábaco/balanza con detalle mecánico puntual |
| N3 — Propiedades | **La fábrica retrofuturista** | máquinas industriales, engranajes, bloques, balanza de laboratorio, palancas, bancos de prueba | tecnológico por defecto — el espacio más "futurista" del catálogo |
| N4 — Divisibilidad | **El Puerto de la Polis** | muelles, barcos, cargamento, rutas (Atenas/Corinto/Delos/Mileto/Rodas/Esparta), tablillas de cera | instrumentos de navegación con detalle mecánico puntual |

Retrofuturismo = Grecia clásica auténtica + toques mecánicos puntuales con sentido
narrativo, nunca sci-fi saturado. **Para un N5 nuevo: elegir un quinto espacio físico
griego que no se solape con los 4 anteriores** (ideas no usadas: biblioteca/archivo,
observatorio, anfiteatro, gimnasio/palestra, templo/oráculo) y fijar su propio banco de
vocabulario antes de escribir el primer ejemplo.

### Banco de contextos por nivel (auditar antes de reutilizar)

Regla dura de todo el catálogo: **ningún objeto concreto se repite más de 2 veces dentro
del mismo nivel**, y conviene revisar también entre niveles. Antes de escribir un ejemplo,
`grep` el objeto candidato en `prealgebra.py` para confirmar cuántas veces aparece hoy —
esta tabla es un snapshot, se desactualiza en cuanto se escribe contenido nuevo.

- **N1 (ágora)**: tablillas, cestas, ciudadanos, cofre de ofrendas, varas de medir,
  cinceles, consejo de la ciudad, mármol, taller del cantero, panes, diagonal de plaza
  empedrada, losa de mármol, columna en tramos, círculo trazado en la plaza, camino de
  baldosas.
- **N2 (mercado)**: rollos de tela, higos, monedas de plata, dracmas/deuda, piezas de
  cerámica, bolsas de especias, tinajas de cerámica, aceitunas, panes, aprendices, medidas
  de aceite, sacos de grano, puesto cuadrado, losas de mármol. Aceitunas/higos ya rondan
  6–12 usos totales — no sumar más sin revisar.
- **N3 (fábrica)**: bloques, engranaje, balanza de laboratorio, pieza de prueba. (Ánforas,
  dracmas y mercader eran objetos de ágora/mercado colados por error — ya corregidos, no
  reintroducir vocabulario de otros niveles aquí.)
- **N4 (puerto)**: ánforas de aceite, sacos de trigo, rollos de tela, cerámica, naranjas,
  tejas, columnas de mármol, postes con tablillas de ruta, canicas, caramelos, entradas de
  feria, remos.

---

## 2. Identidad visual de KatIA (constante en todos los niveles)

KatIA es una **gata cyborg griega** — nunca cambia de especie, nunca contextos ajenos a
Grecia clásica (nada de pizza, nada de objetos modernos). Descripción canónica, reutilizada
palabra por palabra en todos los prompts de imagen:

> Gata blanca con mancha naranja/negra en la cabeza, ojo verde visible, ocular mecánico
> teal en el otro ojo, pata/brazo mecánico, túnica morada y ornamentos dorados.

Variación permitida por nivel: en N3 (fábrica) puede sumar un delantal/arnés de trabajo
discreto, sin tapar la silueta ni reemplazar la túnica. En los demás niveles, sin add-ons.

**Personajes secundarios** (mercader, escriba, aprendiz, niño, mozo, vendedor, mensajero,
etc.) siempre son **animales antropomórficos**, preferentemente otros gatos bípedos con
túnicas/delantales griegos, pelajes variados (atigrado, negro, gris, calicó, siamés,
naranja, blanco moteado). Nunca humanos realistas.

---

## 3. Estructura fija de pantalla ("el guión") por nivel

Cada nivel tiene un **orden de secciones fijo** que no se reordena ni se mezcla entre
niveles. Dos patrones de header distintos, intencionalmente diferentes:

1. **Header de nivel/hub** (`.level-presentation-header` + `.level-presentation-media`) —
   sin caja, kicker + `h1` + intro, imagen ancha 16:9 debajo. Usado en la pantalla-hub de
   cada nivel grande.
2. **Apertura de nodo** (`KatiaStorySlot`) — con caja (borde + gradiente sutil), layout a 2
   columnas (imagen | copy): `eyebrow/title/body` + `question` (pregunta problematizadora)
   + `formulas` opcional. Nunca fusionar los dos patrones.

### N1 — Conjunto numérico (nodo de referencia: B06 Racionales)

```
Encabezado sin caja (max-width 760px)
→ Escalera (<SetNodeScene>)
→ KatiaStorySlot: apertura narrativa + pregunta problematizadora
→ Fila 2 col: [ Descubrimiento guiado | Definición formal ]
→ Ejemplos resueltos standalone, 3 tarjetas — la 3.ª SIEMPRE es la trampa común
→ Ejercicios (práctica existente)
→ Footer
```
Sin escalera de cierre (son los conjuntos, no hay "validez" que cerrar). Toda la copy vive
en i18n (`prealgebra.n1.bXX.story.*`, paridad es/en obligatoria).

### N2 — Operación extendida a los 6 conjuntos (nodo de referencia: E04 División)

```
KatiaStorySlot (apertura + pregunta)
→ [ Descubrimiento guiado | Definición formal ]
→ Ejemplos resueltos 2 columnas (uno por conjunto donde la operación es interesante)
→ Trampa en columna ancha, debajo (trap: True)
→ Escalera de cierre — SIEMPRE 6 filas: ℕ ℤ ℚ 𝕀 ℝ ℂ
→ Práctica (situations, cruza conjuntos, respuestas finitas tecleables)
→ Footer
```
Contenido data-driven en `_N2_OPERATION_CONTENT`, `story_contract.type ==
"unified_set_extension"`.

### N3 — Propiedad/máquina (nodo de referencia: M05 Inversos; M01 para el caso "por operación")

Mismo esqueleto que N2 (mismo renderer/CSS), pero la **escalera de cierre es mixta**:
- M01–M04 (conmutativa/asociativa/distributiva/neutro): cierre **por operación** (+, −, ×,
  ÷), fila = `{symbol: "+", name: "Suma", closed: "yes"/"no", latex, note}`.
- M05 (inversos): cierre **por conjunto**, igual forma que N2 (6 filas ℕ→ℂ), porque lo que
  cambia por conjunto es el opuesto/recíproco de cada número.

`operation_groups` (no `situations`) para la práctica: pares de operaciones que **terminan**
en ambos órdenes (evitar `4÷12=0,333…`, bug ya corregido que bloqueaba `node_completed`).

### N4 — Concepto de divisibilidad (nodo de referencia: C01 Divisibilidad)

```
KatiaStorySlot (Puerto de la Polis, solo telón de fondo — NO fuerza cada ejemplo a "barcos")
→ [ Descubrimiento guiado | Definición formal ]
→ Ejemplos resueltos 2 columnas + trampa ancha (reusa clases .n2-* de N2)
→ Caja de formalización (.n4-formalization) — objeto {title, intro, items:[{label, rule, latex?}]}
→ Práctica MIXTA (numeric + single_select + multi_select en la MISMA lista)
→ Cierre → Footer
```
Sin escalera de conjuntos (no aplica a divisibilidad). Práctica registrada con
`_register_mixed_interactions()` (único registrador nuevo; `evaluate_interaction()` no se
tocó). El hub (`C00`) es la antesala enriquecida: bienvenida + rompe-hielo de 3 escenarios +
selector de 6 muelles — no hay nodos B01/B02/B03 separados como en otros niveles.

---

## 4. Lógica de los ejemplos resueltos (igual en los 4 niveles)

1. **La última tarjeta / la marcada `trap: True` es SIEMPRE la trampa común** — un error
   conceptual real (contraejemplo que desmiente una generalización apresurada), nunca un
   despiste tipográfico. Ejemplos ya usados: N1 B0X (misconception propia del conjunto), N2
   "𝕀 no es cerrado bajo ninguna operación" (`√2+(-√2)=0 ∈ ℚ`, `√2·√2=2 ∈ ℚ`), N3 "opuesto ≠
   recíproco", N4 "par ⇏ divisible por 4".
2. **Diferenciación mínima**: ningún caso concreto (mismos números + mismo contexto) se
   repite entre apertura, descubrimiento, ejemplos resueltos y práctica dentro de un mismo
   nodo. Auditar solapamientos al terminar — bug real: mostrar `12÷4` de ejemplo y volver a
   pedir `12÷4` en la práctica.
3. **LaTeX explícito que compile en KaTeX**: `\dfrac`, `\tfrac`, `\sqrt`, `\cdot`, `\times`,
   `\div`, `\neq`, `\in`/`\notin`, `\mathbb{}`. Coma decimal es-CO con llave: `2{,}5`.
   Verificar 0 `.katex-error` en el render real (los screenshots del preview se cuelgan en
   páginas KaTeX-pesadas — verificar por DOM/`preview_snapshot`).
4. **Feedback específico y accionable**, nunca "correcto/incorrecto" a secas. Cada opción
   incorrecta explica *por qué* está mal (`fb_c01_qN_x`, `misconception_by_option`).

### La tabla de cierre (N2/N3-M05): tema recurrente obligatorio

**𝕀 (irracionales) no es cerrado bajo NINGUNA operación aritmética** — el resultado siempre
puede "caerse" a ℚ (`√2+(-√2)=0`, `√2·√2=2`, `√2÷√2=1`). Esta es la trampa profunda que
motiva por qué ℝ = ℚ ∪ 𝕀, y se repite en suma/resta/multiplicación/potenciación/división. La
radicación es la excepción: su eje es el inverso — *produce* irracionales y motiva ℝ y ℂ.

Tabla resumen de qué conjunto rompe en cada operación (de
`PROMPT_N2_extension_conjuntos.md`, ya verificada):

| Operación | Rompe en | Ejemplo del quiebre |
|---|---|---|
| Suma | 𝕀 | `√2+(-√2)=0 ∈ ℚ` |
| Resta | ℕ (motiva ℤ) y 𝕀 | `3-5=-2 ∉ ℕ`; `√2-√2=0 ∈ ℚ` |
| Multiplicación | 𝕀 | `√2×√2=2 ∈ ℚ` |
| Potenciación | ℤ, ℚ, 𝕀 (según el exponente) | `2^{-2}=1/4` (a ℚ); `2^{1/2}=√2` (a ℝ irracional) |
| Radicación | ℕ, ℤ, ℚ (produce 𝕀); ℂ motivada por radicando negativo | `√2 ∉ ℚ`; `√{-1}=i` |

Para un **N5 con operaciones/propiedades nuevas**: preguntarse primero "¿qué conjunto se
rompe con esta operación y por qué?" — esa pregunta ES el guión del nodo, no un adorno.

---

## 5. Lógica de la práctica (todos los niveles)

- **Respuestas numéricas tecleables**: backend valida con regex `-?\d{1,6}(,\d{1,4})?` —
  solo enteros o decimales de ≤4 cifras, coma decimal es-CO. Nunca periódicos/irracionales
  sin redondear. Elegir números que den resultado finito (`√8÷√2=2`, `9^{1/2}=3`).
- **`multi_select`: `valid_options`/`expected`/`trap_options` son LISTAS, nunca `set()` de
  Python** — viven dentro de `content`, que se serializa a JSON hacia el frontend; un `set`
  no serializa determinísticamente. Bug ya cometido y corregido en N4.
- **Tipos mixtos en una sola lista de práctica** (patrón N4): `numeric` / `single_select` /
  `multi_select` conviven en `practice`, registrados con un único
  `_register_mixed_interactions()`.
- **Descomposición sucesiva** (factorización/MCD/MCM por pasos, N4 C04–C06): se modela como
  **una interacción `numeric` por paso** dentro de `practice`, nunca un widget de árbol
  nuevo — el `worked_example` con `steps` ya muestra la secuencia completa; la práctica
  puede pedir 1–2 pasos sueltos o el resultado final.
- **`validation_status`** marca el estado del nodo: `"F{N}_TODO_stub"` (mínimo viable) →
  `"F{N}_{ID}_pilot"` (enriquecido/verificado). Actualizar al terminar.

---

## 6. Representación gráfica — lógica de los prompts de imagen

Viven en `Implementacion/image-prompts/n{1..4}-<espacio>.md`, un archivo por nivel, una
entrada por nodo/ejemplo con `image_slot: True`. Cada archivo repite una cabecera fija y
luego una entrada por escena. Estructura de cada entrada:

```
## <NODO> — <título>
**<Componente>** (<eyebrow/imagen de referencia>, <aspect ratio>) — de `<campo del dict>`: "<texto fuente citado, no inventado>"

> <descripción de la escena: quién, qué objetos, qué acción, qué NO se debe mostrar>
> Estilo base + aspect ratio <N>:<N>.
```

### 6.1 — Estilo base (una cola compartida, con matices por espacio)

Todos los prompts terminan con la misma cola de estilo, ajustada solo en el "espacio se lee
como...":

> *pixel-art educativo refinado, estilo 16/32-bit narrativo de alta calidad, con clusters de
> píxeles visibles, bordes pixelados limpios, sombreado por bloques y dithering sutil; NO
> pintura digital hiperrealista.* KatIA legible en primer/medio plano, escena contenida,
> pocos personajes secundarios, objetos pedagógicos claros sobre [mostrador/mesa/banco de
> trabajo/muelle según el nivel], sombras azul noche, luz dorada de lámpara/antorcha/farol,
> mármol/piedra/madera cálida y acentos teal pequeños en el ocular de KatIA o en
> instrumentos. + identidad de KatIA (§2) + cómo se lee el espacio del nivel (§1).

Referencias de línea gráfica obligatorias (adjuntar o citar si la herramienta lo permite):
`Implementacion/image-prompts/referencias/step-naturales.png`, `step-enteros.png`, `step-racionales.png`,
`step-reales.png`, `escalera-conjuntos.png`, `katia-primer-plano-enteros.png`,
`caso-enteros-recta.jpg`. **Antes de inventar un estilo nuevo para un nivel nuevo: mirar
estas imágenes existentes** — es la lección aprendida ya guardada en memoria
(`feedback-image-prompts-check-existing-art`).

### 6.2 — Reglas duras (no negociables, iguales en los 4 niveles)

1. **El prompt describe la SITUACIÓN, nunca la SOLUCIÓN** (mismo espíritu que V2-R9: la
   respuesta correcta nunca viaja al frontend). Nunca escribir el resultado numérico en la
   escena, ni dibujar exactamente la cantidad de objetos que resuelve el ejercicio contando.
   Ejemplo correcto: para "¿cuántos ladrillos hay en 3 filas de 4?" se describe al albañil
   apilando ladrillos en filas, nunca se muestran 12 ladrillos contables ni el número "12".
2. **Escaleras/peldaños/escalinatas en la imagen deben estar limpios**: sin símbolos,
   letras, números, runas, marcas, medallones, flechas ni relieves matemáticos.
3. **Negativos de estilo estándar**: no panorama épico, no multitudes, no sci-fi duro, no
   pintura digital lisa, no neón saturado, no anime/chibi, no humanos realistas, no cambiar
   a KatIA por una gata totalmente metálica.
4. **Aspect ratio por tipo de imagen**: header de nivel/hub → 16:9 (ancho completo);
   `KatiaStorySlot` de nodo → ~4:3 (columna imagen | copy); ejemplo resuelto / ítem de
   práctica → ~1:1 (cuadrado).
5. Los datos de la escena (objetos, cantidades vagas, personajes) se **citan del texto ya
   escrito** (`katia.body`, `worked_example.statement`, `item.story`/`support_objects`) —
   nunca se inventan objetos nuevos que no estén en el dict.

### 6.3 — Historia + imagen en un ítem de práctica suelto (patrón introducido en N4)

Para dar contexto a un ítem que hoy es abstracto, se agregan 3 campos opcionales al dict del
ítem en vez de reescribirlo entero:

```python
{
    "id": "ICE2", "kind": "single_select",
    "story": "1-3 frases que narran la situación en el mundo del nivel",
    "image_slot": True,
    "support_objects": ["objeto concreto 1", "objeto concreto 2"],  # 2-4, brief para el arte
    "prompt": "...", "options": [...],
}
```
`story` solo si el `prompt` original es abstracto (si ya trae la historia incrustada, basta
`image_slot: True`). `image_slot` se pone en casi todo ítem narrativo — es barato y marca la
intención de ilustrar aunque no exista el arte todavía. Render vía `storyBlock` en
`PracticeItem` (`LevelFourLesson.tsx`), reutilizable en cualquier práctica nueva.

---

## 7. Invariantes no negociables — checklist antes de dar un nodo por terminado

- [ ] Vocabulario del espacio correcto, cero cruces con otro nivel (§1)
- [ ] KatIA con identidad visual canónica, sin desviaciones no permitidas (§2)
- [ ] Orden de secciones exacto del nivel, sin reordenar ni mezclar patrones (§3)
- [ ] Última tarjeta / `trap: True` = error conceptual real, no despiste (§4)
- [ ] Ningún caso concreto repetido entre apertura/descubrimiento/ejemplos/práctica (§4)
- [ ] LaTeX compila, 0 `.katex-error` verificado por DOM (§4)
- [ ] Feedback específico por opción incorrecta, nunca genérico (§4)
- [ ] Si aplica escalera: 6 filas ℕ ℤ ℚ 𝕀 ℝ ℂ, tema 𝕀-no-cerrado presente (§4)
- [ ] Respuestas numéricas finitas, regex-válidas; `multi_select` con listas, no `set()` (§5)
- [ ] Objeto concreto usado ≤2 veces en el nivel — `grep` antes de reutilizar (§1)
- [ ] Prompts de imagen: situación no solución, escaleras limpias, aspect ratio correcto (§6)
- [ ] `validation_status` actualizado

---

## 8. Cómo arrancar un nivel nuevo (N5+)

1. Elegir el espacio físico (§1) — no reutilizar vocabulario de N1–N4.
2. Decidir si el nuevo contenido encaja en un `story_contract.type` existente
   (`unified_set_extension`, `guided_discovery_formalization`) o si necesita uno genuinamente
   nuevo. Si reutiliza un tipo existente, **reutilizar el renderer/CSS también** — el trabajo
   nuevo es solo contenido en un dict `_N{X}_..._CONTENT`, igual que N2→N3 y N1→N4.
3. Solo si el formato es realmente distinto (otra secuencia de secciones, otro tipo de
   escalera/cierre) se justifica tocar `LevelXLesson.tsx`/`.css` — eso es cambio de
   arquitectura, no de contenido, y conviene confirmarlo antes con el usuario.
4. Escribir el primer nodo como **piloto** (`validation_status: "F{N}_..._pilot"`), pasar el
   checklist de §7, y solo después replicar a los nodos restantes del nivel.
5. Escribir los prompts de imagen del nodo piloto en
   `Implementacion/image-prompts/n{N}-<espacio>.md` siguiendo la cabecera de estilo de §6.1
   (mirar las 4 existentes como plantilla de tono, no copiar el vocabulario ajeno).
