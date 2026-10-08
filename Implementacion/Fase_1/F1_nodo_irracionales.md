# Nodo: Números irracionales — decimales que no se repiten
**ID:** PREALG-N1-B07-IRRACIONALES-DECIMALES

---

## PARTE A — Especificación legible

### A1. Metadatos del nodo

| Campo | Valor |
|---|---|
| **ID técnico** | PREALG-N1-B07-IRRACIONALES-DECIMALES |
| **Título visible** | Irracionales: decimales que no se repiten |
| **Módulo** | Preálgebra |
| **Nivel** | Nivel 1 — Conjuntos numéricos |
| **Tipo de nodo** | Nodo circular principal con camino opcional de profundización (√2) |
| **Ubicación en la ruta** | Cuarto nodo numérico; se desbloquea tras completar B06 (Racionales) |
| **Función pedagógica** | Introducir los irracionales como números reales que **no pueden escribirse como fracción de enteros**, partiendo de la comparación con decimales racionales |
| **Objetivo de aprendizaje** | El estudiante diferencia decimales racionales (exactos o periódicos) de decimales infinitos no periódicos, y reconoce estos últimos como irracionales |
| **Microhabilidades** | • Diferenciar decimal exacto / periódico / infinito no periódico<br>• Reconocer que no todo decimal infinito es irracional<br>• Reconocer que los irracionales no pueden escribirse como fracción de enteros<br>• Identificar π y √2 como irracionales<br>• Entender que una aproximación no es el valor exacto<br>• Distinguir la notación I de irracionales de la unidad imaginaria i |
| **Misconception tags** | cree_que_todo_decimal_infinito_es_irracional<br>confunde_aproximacion_con_valor_exacto<br>clasifica_decimal_periodico_como_irracional<br>no_reconoce_irracional_como_real<br>cree_que_irracional_no_existe<br>confunde_I_irracionales_con_i_imaginaria<br>confunde_sqrt2_con_aproximacion_decimal |
| **Referencias de refuerzo** | PREALG-N1-B06-RACIONALES-FRACCION-DIVISION<br>PREALG-N1-B08-REALES-RECTA<br>PREALG-N1-B10-CLASIFICADOR-BASICO<br>PREALG-N1-B11-CLASIFICADOR-RIGUROSO<br>PREALG-N1-B12-DETECTIVE-FALSEDADES |

> **⚠ CORRECCIÓN CLAVE APLICADA:** La definición de irracional se ancla en **"no puede escribirse como fracción de enteros"** (criterio estructural), NO en "el decimal no termina/no se repite" (criterio observacional, que es solo una consecuencia). Esto evita la misconception de que basta con ver muchos decimales para clasificar como irracional.

---

### A2. Guión de pantalla (texto íntegro por pantalla)

#### 2.1 Encabezado

**Texto visible:**
```
Irracionales: decimales que no se repiten
```

**Subtítulo:**
```
No todos los decimales infinitos vienen de una fracción.
```

---

#### 2.2 Diálogo inicial de Katia

**Contexto visual:** Katia aparece junto al cuarto peldaño de la escalera.

**Diálogo de Katia:**
```
En el bloque anterior vimos que algunas fracciones producen decimales 
exactos, como:

1/4 = 0.25

y otras producen decimales periódicos, como:

1/3 = 0.333…

Pero ahora aparece una nueva pregunta:

¿todos los números decimales vienen de una fracción?
```

---

#### 2.3 Activación conceptual

**Título visible:**
```
Comparemos tres tipos de decimales
```

**Texto visible:**
```
Observa estos ejemplos:
```

**Tabla comparativa:**

| Tipo de decimal | Ejemplo | ¿Qué ocurre? |
|---|---|---|
| Decimal exacto | 0.25 | Termina |
| Decimal periódico | 0.333… | No termina, pero repite un patrón |
| Decimal infinito no periódico | 3.14159265… | No termina y no repite un patrón |

**Diálogo de Katia:**
```
Los dos primeros pueden venir de fracciones.

El tercero se comporta distinto: no termina y no tiene un patrón que se repita.
```

---

#### 2.4 Interacción 1 — Reconocer el patrón

**Pregunta visible:**
```
¿Cuál de estos decimales es periódico?
```

**Opciones de respuesta:**
- 0.25
- 0.333…
- 3.14159265…

**Respuesta esperada:** 0.333…

---

#### 2.5 Retroalimentación para Interacción 1

##### Si responde **0.333…**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
0.333… es periódico porque el 3 se repite indefinidamente.

Además:

0.333… = 1/3

Por eso es racional, no irracional.
```

##### Si responde **0.25**

**Título del recuadro:**
```
⚠ Ese decimal termina
```

**Retroalimentación de Katia:**
```
0.25 es un decimal exacto porque termina.

También es racional, porque:

0.25 = 1/4
```

##### Si responde **3.14159265…**

**Título del recuadro:**
```
⚠ No hay repetición periódica
```

**Retroalimentación de Katia:**
```
3.14159265… continúa indefinidamente, pero sus cifras no repiten un patrón fijo.

Ese tipo de decimal es infinito no periódico.
```

**Misconception tag registrado:** `confunde_decimal_periodico_con_no_periodico`

---

#### 2.6 Ejemplo principal: π

**Título visible:**
```
Un ejemplo famoso: π
```

**Texto visible:**
```
Cuando estudiamos círculos, aparece un número especial:

π = 3.14159265…

Este número continúa indefinidamente y sus cifras no siguen un patrón periódico.

Por eso, π es un número irracional.
```

**Diálogo de Katia:**
```
Podemos usar aproximaciones de π, como 3.14, pero esas aproximaciones no son 
el valor exacto de π.
```

---

#### 2.7 Pausa conceptual — Aproximación y valor exacto

**Título visible:**
```
Pausa: una aproximación no es el número exacto
```

**Texto visible:**
```
El número:

3.14

es una aproximación racional de π, porque tiene una cantidad finita de decimales.

Pero π exacto es:

π = 3.14159265…

y no termina ni se repite.
```

**Diálogo de Katia:**
```
Esta diferencia es importante: escribir algunos decimales de un número 
irracional no significa que ya tengamos todo el número.
```

---

#### 2.8 Interacción 2 — Aproximación vs exacto

**Pregunta visible:**
```
¿Cuál afirmación es correcta?
```

**Opciones de respuesta:**
- **A.** 3.14 es exactamente igual a π.
- **B.** 3.14 es una aproximación de π.
- **C.** π termina en 3.14.

**Respuesta esperada:** B

---

#### 2.9 Retroalimentación para Interacción 2

##### Si responde **B**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
3.14 es una aproximación de π, no su valor exacto.

π = 3.14159265…

El número continúa indefinidamente.
```

##### Si responde **A**

**Título del recuadro:**
```
⚠ No exactamente
```

**Retroalimentación de Katia:**
```
3.14 no es exactamente igual a π. Es solo una aproximación.

El valor de π continúa con infinitas cifras decimales no periódicas.
```

**Misconception tag registrado:** `confunde_aproximacion_con_valor_exacto`

##### Si responde **C**

**Título del recuadro:**
```
⚠ π no termina
```

**Retroalimentación de Katia:**
```
π no termina en 3.14. Esa es una aproximación corta.

El número exacto tiene infinitas cifras decimales no periódicas.
```

**Misconception tag registrado:** `confunde_aproximacion_con_valor_exacto`

---

#### 2.10 Formalización

**Título visible:**
```
¿Qué son los números irracionales?
```

**Texto visible:**
```
Los números irracionales son números reales que NO pueden escribirse como 
una fracción entre dos enteros.

Es decir:

I = { x ∈ R | x ∉ Q }

También podemos decir que son números reales que no son racionales.

Como consecuencia de no poder escribirse como fracción, sus decimales son 
infinitos y no periódicos.
```

> **[Nota interna — corrección clave]** El criterio definitorio es "no se puede escribir como fracción de enteros". El comportamiento decimal (infinito no periódico) es una **consecuencia** de esa imposibilidad, no la definición misma. El texto refleja esta jerarquía: primero la imposibilidad estructural, luego la consecuencia decimal.

---

#### 2.11 Nota sobre notación

**Título visible:**
```
Nota de notación
```

**Texto visible:**
```
En algunos materiales escolares, los irracionales se denotan con I o con Q'.

En este nivel usaremos principalmente la idea:

"reales que no son racionales"

para evitar confundir la I de irracionales con la i que aparecerá más adelante 
en números complejos.
```

---

#### 2.12 Ejemplos y no ejemplos

**Título visible:**
```
Ejemplos de números irracionales
```

**Texto visible:**
```
π, √2, √3, e
```

**Título visible:**
```
No son irracionales
```

**Texto visible:**
```
0.25, 0.333…, −3, 1/2
```

**Nota de Katia:**
```
0.333… no termina, pero sí repite un patrón. Por eso es racional.
```

---

#### 2.13 Camino opcional — √2

**Título visible:**
```
Reto opcional: √2
```

**Texto visible:**
```
Hay irracionales que aparecen al medir ciertas longitudes.

Por ejemplo, la diagonal de un cuadrado de lado 1 mide exactamente:

√2

La calculadora muestra una aproximación:

1.41421356…

Pero el número exacto es √2, no una aproximación finita como 1.41421.
```

**Diálogo de Katia:**
```
Este camino es opcional. Más adelante, cuando estudies geometría y el teorema 
de Pitágoras, entenderás mejor por qué aparece √2 en la diagonal de un cuadrado.
```

**Botón opcional:**
```
Ver reto de √2
```

**Botón alternativo:**
```
Continuar sin reto
```

---

#### 2.14 Interacción opcional — Aproximación de √2

**Pregunta visible:**
```
¿Cuál de estas expresiones representa el valor exacto de la diagonal del 
cuadrado de lado 1?
```

**Opciones de respuesta:**
- √2
- 1.41421
- 1.4

**Respuesta esperada:** √2

---

#### 2.15 Retroalimentación del camino opcional

##### Si responde **√2**

**Título del recuadro:**
```
✓ Correcto
```

**Retroalimentación de Katia:**
```
√2 representa el valor exacto.

Números como 1.41421 o 1.4 son aproximaciones.
```

##### Si responde **1.41421** o **1.4**

**Título del recuadro:**
```
⚠ Eso es una aproximación
```

**Retroalimentación de Katia:**
```
1.41421 y 1.4 son aproximaciones decimales.

El valor exacto es:

√2
```

**Misconception tag registrado:** `confunde_sqrt2_con_aproximacion_decimal`

---

#### 2.16 Microactividad de cierre (Mini reto)

**Título visible:**
```
Mini reto
```

**Pregunta visible:**
```
Clasifica cada número como racional o irracional.
```

**Elementos (cada uno con opción Racional / Irracional):**

| Número | Opciones |
|---|---|
| 0.5 | Racional / Irracional |
| 0.333… | Racional / Irracional |
| π | Racional / Irracional |
| √2 | Racional / Irracional |
| 7 | Racional / Irracional |

**Respuestas esperadas:**
- 0.5 → **Racional**
- 0.333… → **Racional**
- π → **Irracional**
- √2 → **Irracional**
- 7 → **Racional**

---

#### 2.17 Retroalimentación para el mini reto

##### Si todo está correcto

**Título del recuadro:**
```
✓ Bien
```

**Retroalimentación de Katia:**
```
Correcto. Identificaste que los racionales pueden ser enteros, decimales 
exactos o decimales periódicos.

Los irracionales, como π y √2, tienen decimales infinitos no periódicos 
porque no pueden escribirse como fracción de enteros.
```

---

##### Si clasifica **0.333…** como irracional

**Título del recuadro:**
```
⚠ No todo decimal infinito es irracional
```

**Retroalimentación de Katia:**
```
0.333… es infinito, pero repite el 3.

Como:

0.333… = 1/3

es racional.
```

**Misconception tag registrado:** `cree_que_todo_decimal_infinito_es_irracional`

---

##### Si clasifica **7** como irracional

**Título del recuadro:**
```
⚠ Recuerda los enteros
```

**Retroalimentación de Katia:**
```
7 es racional porque puede escribirse como:

7 = 7/1

Todo entero es racional.
```

**Misconception tag registrado:** `cree_que_enteros_no_son_racionales`

---

##### Si clasifica **π** o **√2** como racional

**Título del recuadro:**
```
⚠ Revisa la repetición
```

**Retroalimentación de Katia:**
```
π y √2 tienen decimales infinitos no periódicos.

No pueden escribirse como fracción de enteros. Por eso son irracionales.
```

**Misconception tag registrado:** `clasifica_decimal_periodico_como_irracional` (inverso)

---

#### 2.18 Mensaje de transición

**Texto visible:**
```
Ahora conocemos dos grandes grupos dentro de la recta numérica: racionales 
e irracionales.
```

**Diálogo de Katia:**
```
Cuando reunimos racionales e irracionales, aparece el conjunto de los 
números reales.
```

**Botón principal:**
```
Ir a reales
```

---

### A3. Storyboard — Flujo visual y de interacción

#### 3.1 Estado inicial

**Contexto del mapa:**
- El mapa enfoca el nodo PREALG-N1-B07-IRRACIONALES-DECIMALES.
- El nodo aparece en estado `actual` tras completar B06 (Racionales).
- Un hexágono de transición conceptual aparece **antes** del nodo:
  ```
  De fracciones a decimales no periódicos
  ```

---

#### 3.2 Entrada de elementos (Secuencia visual)

1. **Aparece el título** "Irracionales: decimales que no se repiten".
2. **Se ilumina el cuarto peldaño** de la escalera.
3. **Katia retoma** los decimales exactos y periódicos del bloque anterior.
4. **Aparece la tabla comparativa** de tipos de decimales (exacto / periódico / infinito no periódico).
5. **Se activa la primera interacción** sobre decimal periódico.
6. **Aparece el ejemplo de π.**
7. **Se muestra la pausa** sobre aproximación y valor exacto.
8. **Se presenta la formalización.**
9. **Se ofrece el camino opcional con √2.**
10. **Se cierra con la microactividad** de clasificación racional/irracional.

---

#### 3.3 Interacción del estudiante (Fase de actividad)

El estudiante realiza esto **en orden secuencial:**

1. **Compara los tres tipos de decimales** (tabla).
2. **Identifica un decimal periódico** (Interacción 1, opción única).
3. **Ve retroalimentación inmediata.**
4. **Lee el ejemplo de π** como decimal infinito no periódico.
5. **Lee la pausa** sobre aproximación vs valor exacto.
6. **Diferencia aproximación y valor exacto** (Interacción 2, opción única A/B/C).
7. **Ve retroalimentación inmediata.**
8. **Lee la formalización** de los irracionales.
9. **Lee la nota sobre notación** (I vs i).
10. **Ve ejemplos y no ejemplos** con nota de Katia.
11. **Decide si toma el camino opcional de √2** (botón "Ver reto" o "Continuar sin reto").
    - **Si toma el reto:** responde la Interacción opcional sobre √2, ve retroalimentación.
    - **Si lo omite:** continúa directamente.
12. **Realiza el mini reto** (clasificar 5 números como racional/irracional).
13. **Ve retroalimentación del mini reto** (diferenciada).
14. **Presiona "Ir a reales"** y el nodo se marca como completado.

---

#### 3.4 Estados de pantalla (Evolución visual)

| Estado | Contenido visible | Controles activos | Nota |
|---|---|---|---|
| **1 — Retoma desde racionales** | 0.25, 0.333… + pregunta "¿todos vienen de fracciones?" | Desplazamiento | Conecta con bloque anterior |
| **2 — Comparación de decimales** | Tabla: exacto / periódico / infinito no periódico | Desplazamiento | Establece la distinción central |
| **3a — Interacción sobre periodicidad** | Pregunta "¿Cuál es periódico?" + 3 opciones | Botones seleccionables | El estudiante identifica |
| **3b — Retroalimentación 1** | Respuesta + Diálogo de Katia | Botón "Siguiente" | Aclara periodicidad |
| **4 — Ejemplo de π** | π = 3.14159265… como infinito no periódico | Desplazamiento | Presenta el irracional emblemático |
| **5 — Aproximación vs exacto** | 3.14 (aproximación) vs π (exacto) | Desplazamiento | Diferencia crítica |
| **6a — Interacción 2** | Pregunta A/B/C + 3 opciones | Botones seleccionables | El estudiante discrimina |
| **6b — Retroalimentación 2** | Respuesta + Diálogo de Katia | Botón "Siguiente" | Aclara aproximación |
| **7 — Formalización** | Definición: irracional = no escribible como fracción | Desplazamiento | Formaliza (criterio estructural) |
| **8 — Notación** | Nota sobre I / Q' vs i imaginaria | Desplazamiento | Evita confusión futura |
| **9 — Ejemplos y no ejemplos** | π, √2, √3, e vs 0.25, 0.333…, −3, 1/2 | Desplazamiento | Refuerza reconocimiento |
| **10 — Camino opcional √2** | Reto de la diagonal del cuadrado | Botón "Ver reto" / "Continuar sin reto" | Decisión del estudiante |
| **10a — Interacción opcional** (si toma) | Pregunta sobre valor exacto + 3 opciones | Botones seleccionables | El estudiante elige √2 |
| **10b — Retroalimentación opcional** (si toma) | Respuesta + Diálogo de Katia | Botón "Continuar" | Aclara valor exacto |
| **11a — Mini reto** | Clasificar 5 números (racional/irracional) | Toggles por número | El estudiante clasifica |
| **11b — Retroalimentación del reto** | Resultado + Diálogo de Katia diferenciado | Botón "Continuar" | Cierra con refuerzo |
| **12 — Transición** | Mensaje + botón "Ir a reales" | Botón navegable | Prepara el siguiente nodo |

---

#### 3.5 Eventos visuales y animaciones (Framer Motion)

- **Entrada del nodo:** Fade-in del título y hexágono de transición.
- **Katia aparece:** Slide-in lateral + delay.
- **Tabla comparativa:** Filas entran en stagger (exacto → periódico → no periódico).
- **Ejemplo de π:** Los decimales de π se "despliegan" con animación que sugiere infinitud.
- **Aproximación vs exacto:** Visual que contrasta "3.14" (caja cerrada) vs "π = 3.14159…" (caja que se extiende).
- **Camino opcional √2:** El cuadrado de lado 1 aparece, su diagonal se ilumina mostrando √2.
- **Retroalimentación:** Slide-down con cambio de color.
- **Formalización se destaca:** Recuadro con borde sutil que brilla.
- **Mini reto:** Toggles animados; al clasificar correctamente, cada número se ilumina.
- **Transición final:** El peldaño se marca completado y el hexágono siguiente se ilumina.

---

#### 3.6 Relación con el mapa visual

**Nodo circular:**
- Representa la pantalla principal de irracionales (B07).
- Estado: `actual` → `completado`.
- **Camino opcional** (√2): representado como una ramificación visual (puntico opcional-explorable).

**Punticos internos (eventos registrados):**
- Visualizó comparación de decimales
- Respondió decimal periódico
- Visualizó ejemplo de π
- Visualizó pausa aproximación/exacto
- Respondió aproximación vs exacto
- Vio formalización
- Vio nota de notación
- **Tomó/omitió camino opcional √2**
- (Si tomó) Respondió reto de √2
- Resolvió mini reto
- Vio retroalimentación
- Completó nodo

**Hexágono de transición (posterior):**
- Texto: "Reunir racionales e irracionales"
- Conecta hacia: PREALG-N1-B08-REALES-RECTA
- Se ilumina al completar B07.

---

### A4. Diferenciación por nivel (Básico / Intermedio / Avanzado)

| Aspecto | Básico | Intermedio | Avanzado |
|---|---|---|---|
| **Tabla comparativa** | Con explicación detallada por fila | Tabla estándar | Tabla compacta |
| **Ejemplo de π** | Desarrollado con muchos decimales visibles | Estándar | Breve |
| **Camino opcional √2** | Recomendado, con apoyo visual | Disponible | Recomendado como extensión avanzada |
| **Divulgación de formalización** | Expandida por defecto | Colapsada inicialmente | Colapsada |
| **Mini reto** | 5 números estándar | 5 números estándar | Variante: incluye √4 (truco: es racional=2), 0.101001000…, golden ratio φ |
| **Pistas disponibles** | Máximo | Medio | Mínimo |

> **Nota sobre el avanzado:** Incluir √4 en el mini reto avanzado es deliberado — fuerza al estudiante a reconocer que √4 = 2 (racional), evitando la sobregeneralización "toda raíz es irracional".

---

### A5. Notas pedagógicas inline

**[NOTA PEDAGÓGICA — Definición estructural, no observacional]**
La corrección central de este nodo: un irracional se define por **no poder escribirse como fracción de enteros**, no por "tener muchos decimales" o "el decimal no termina". El comportamiento decimal (infinito no periódico) es la *consecuencia observable* de esa imposibilidad estructural. Anclar la definición en el criterio estructural previene que estudiantes clasifiquen por apariencia superficial.

**[NOTA PEDAGÓGICA — Aproximación ≠ valor exacto]**
La distinción entre 3.14 (aproximación racional) y π (irracional exacto) es conceptualmente difícil. Los estudiantes tienden a creer que "escribir más decimales" eventualmente "captura" el número. El nodo refuerza que ninguna cantidad finita de decimales iguala al irracional.

**[NOTA PEDAGÓGICA — Notación I vs i]**
La nota anticipatoria sobre la notación (evitar I para no confundir con la i imaginaria de B09) es una decisión de coherencia curricular. Prepara el terreno para los complejos sin crear ambigüedad simbólica.

**[NOTA PEDAGÓGICA — Camino opcional como gating suave]**
El reto de √2 es opcional y no bloquea el progreso. Esto respeta la heterogeneidad del grupo: estudiantes que aún no han visto Pitágoras pueden continuar sin frustración, mientras que los avanzados profundizan.

---

### A6. Accesibilidad

- **Colores:** No dependen únicamente de rojo/verde; se usan símbolos ✓ y ⚠.
- **Tabla comparativa:** Headers semánticos, aria-labels.
- **Matemática:** π se anuncia como "pi"; √2 como "raíz cuadrada de dos"; 0.333… como "cero punto tres periódico".
- **Símbolos:** ∈, ∉, R, Q, I con etiquetas ARIA.
- **Camino opcional:** Claramente etiquetado como opcional para lectores de pantalla.
- **Contraste:** Relación mínima 4.5:1.

---

### A7. Notas de citas pedagógicas

- **Misconception de irracionales:** Sirotic & Zazkis (2007) — los estudiantes confunden "infinito" con "irracional" y aproximaciones con valores exactos.
- **Naturaleza de los irracionales:** Fischbein, Jehiam & Cohen (1995) — dificultades intuitivas con la incompletitud de los racionales.
- **Aproximación vs exacto:** Zazkis & Sirotic (2004) — la representación decimal puede ocultar la naturaleza del número.
- **Camino opcional (productive struggle):** Kapur (2008) — el reto opcional de √2 ofrece "fracaso productivo" sin penalización.

---

### A8. Handoff a Claude Design

**Componentes clave:**
- [componente-katia-dialogo]
- [componente-tabla-comparativa-decimales]
- [componente-pregunta-opcion-unica]
- [componente-decimal-infinito-animado] — Despliegue de decimales de π/√2
- [componente-aproximacion-vs-exacto] — Visual contrastante
- [componente-camino-opcional] — Bifurcación con dos botones
- [componente-cuadrado-diagonal] — Visualización geométrica de √2
- [componente-mini-reto-clasificacion] — Toggles racional/irracional
- [componente-retroalimentacion-modal]
- [componente-formalización-expandible]
- [componente-ejemplos-tarjetas]
- [componente-transicion-hexagono]

**Tokens del sistema de diseño:**
- Acentos: morado (primario), teal (secundario)
- Tipografía: sans-serif para body, serif para títulos
- Animaciones: Framer Motion

**Render bloqueante:**
- Verificar render de: π, √2, √3, √4, e, 0.25, 0.333…, 3.14, 3.14159265…, 1.41421356…, 1/4, 1/3, 7/1
- Verificar símbolos ∈, ∉, R, Q, I, Q' se muestran correctamente.
- Verificar que √ (radical) se renderiza con la línea superior correcta.

---

## PARTE B — Especificación técnica (JSON)

```json
{
  "node_id": "PREALG-N1-B07-IRRACIONALES-DECIMALES",
  "node_type": "conceptual_content_with_optional_branch",
  "name": "Irracionales: decimales que no se repiten",
  "position_in_route": "ruta_nucleo_fourth_numeric_set",
  "unlock_rule": "completed_node:PREALG-N1-B06-RACIONALES-FRACCION-DIVISION",
  "unlock_after": 0,
  "skip_penalty": false,
  "node_state": "bloqueado",
  "affects_elo": false,
  "safe_zone": true,
  "has_optional_branch": true,

  "mathematical_content": {
    "primary_set": "I",
    "definition_PRIMARY": "Números reales que NO pueden escribirse como fracción de dos enteros",
    "definition_consequence": "Como consecuencia, sus decimales son infinitos y no periódicos",
    "convention": "I = { x ∈ R | x ∉ Q }",
    "notation_note": "Se evita usar I sola para no confundir con la unidad imaginaria i (B09)",
    "examples": ["π", "√2", "√3", "e"],
    "critical_correction": "La definición es ESTRUCTURAL (no escribible como fracción), NO observacional (decimal no periódico). El comportamiento decimal es consecuencia, no definición."
  },

  "pedagogical_structure": {
    "phase_1_activation": {
      "name": "Comparación de tres tipos de decimales",
      "comparison_table": [
        {"tipo": "Decimal exacto", "ejemplo": "0.25", "comportamiento": "Termina"},
        {"tipo": "Decimal periódico", "ejemplo": "0.333…", "comportamiento": "No termina, pero repite un patrón"},
        {"tipo": "Decimal infinito no periódico", "ejemplo": "3.14159265…", "comportamiento": "No termina y no repite un patrón"}
      ],
      "educator_note": "Los dos primeros pueden venir de fracciones. El tercero no termina y no tiene patrón que se repita.",
      "interactions": [
        {
          "interaction_id": "I1_reconocer_periodico",
          "type": "single_choice",
          "question": "¿Cuál de estos decimales es periódico?",
          "options": ["0.25", "0.333…", "3.14159265…"],
          "expected_answer": "0.333…",
          "feedback": {
            "correct": "0.333… es periódico porque el 3 se repite indefinidamente.\nAdemás:\n0.333… = 1/3\nPor eso es racional, no irracional.",
            "0.25": "0.25 es un decimal exacto porque termina.\nTambién es racional, porque:\n0.25 = 1/4",
            "3.14159265…": "3.14159265… continúa indefinidamente, pero sus cifras no repiten un patrón fijo.\nEse tipo de decimal es infinito no periódico."
          }
        }
      ]
    },

    "phase_2_pi_example": {
      "name": "Ejemplo principal: π",
      "content": "π = 3.14159265… es un decimal infinito no periódico, por eso es irracional.",
      "educator_note": "Podemos usar aproximaciones de π, como 3.14, pero esas aproximaciones no son el valor exacto de π.",
      "pausa_aproximacion": {
        "name": "Pausa: una aproximación no es el número exacto",
        "content": "3.14 es una aproximación racional de π (finita). Pero π exacto = 3.14159265… no termina ni se repite.",
        "educator_note": "Escribir algunos decimales de un número irracional no significa que ya tengamos todo el número."
      },
      "interactions": [
        {
          "interaction_id": "I2_aproximacion_vs_exacto",
          "type": "single_choice",
          "question": "¿Cuál afirmación es correcta?",
          "options": [
            "A. 3.14 es exactamente igual a π.",
            "B. 3.14 es una aproximación de π.",
            "C. π termina en 3.14."
          ],
          "expected_answer": "B",
          "misconceptions_detected": ["confunde_aproximacion_con_valor_exacto"],
          "feedback": {
            "correct": "3.14 es una aproximación de π, no su valor exacto.\nπ = 3.14159265…\nEl número continúa indefinidamente.",
            "A": "3.14 no es exactamente igual a π. Es solo una aproximación.\nEl valor de π continúa con infinitas cifras decimales no periódicas.",
            "C": "π no termina en 3.14. Esa es una aproximación corta.\nEl número exacto tiene infinitas cifras decimales no periódicas."
          }
        }
      ]
    },

    "phase_3_formalization": {
      "name": "Formalización",
      "title": "¿Qué son los números irracionales?",
      "definition": "Los números irracionales son números reales que NO pueden escribirse como una fracción entre dos enteros.",
      "symbolic_representation": "I = { x ∈ R | x ∉ Q }",
      "consequence": "Como consecuencia de no poder escribirse como fracción, sus decimales son infinitos y no periódicos.",
      "notation_note": "En algunos materiales se denotan con I o Q'. En este nivel usamos 'reales que no son racionales' para evitar confundir I con la i imaginaria (complejos).",
      "expandable": true,
      "default_state_by_level": {
        "basico": "expanded",
        "intermedio": "collapsed",
        "avanzado": "collapsed"
      }
    },

    "phase_4_examples": {
      "name": "Ejemplos y no ejemplos",
      "examples": ["π", "√2", "√3", "e"],
      "non_examples": ["0.25", "0.333…", "−3", "1/2"],
      "educator_note": "0.333… no termina, pero sí repite un patrón. Por eso es racional."
    },

    "phase_5_optional_branch": {
      "name": "Camino opcional: √2",
      "is_optional": true,
      "blocks_progress": false,
      "content": "La diagonal de un cuadrado de lado 1 mide exactamente √2. La calculadora muestra 1.41421356…, pero el valor exacto es √2, no una aproximación finita.",
      "educator_note": "Este camino es opcional. Más adelante, en geometría y Pitágoras, se entiende por qué aparece √2.",
      "interaction": {
        "interaction_id": "I_OPT_sqrt2_exacto",
        "type": "single_choice",
        "question": "¿Cuál de estas expresiones representa el valor exacto de la diagonal del cuadrado de lado 1?",
        "options": ["√2", "1.41421", "1.4"],
        "expected_answer": "√2",
        "misconceptions_detected": ["confunde_sqrt2_con_aproximacion_decimal"],
        "feedback": {
          "correct": "√2 representa el valor exacto.\nNúmeros como 1.41421 o 1.4 son aproximaciones.",
          "incorrect": "1.41421 y 1.4 son aproximaciones decimales.\nEl valor exacto es:\n√2"
        }
      }
    },

    "phase_6_mini_challenge": {
      "name": "Mini reto",
      "type": "classification_grid",
      "question": "Clasifica cada número como racional o irracional.",
      "items": [
        {"value": "0.5", "expected": "racional"},
        {"value": "0.333…", "expected": "racional"},
        {"value": "π", "expected": "irracional"},
        {"value": "√2", "expected": "irracional"},
        {"value": "7", "expected": "racional"}
      ],
      "feedback_by_error_pattern": {
        "correct_all": {
          "title": "✓ Bien",
          "body": "Correcto. Identificaste que los racionales pueden ser enteros, decimales exactos o decimales periódicos.\nLos irracionales, como π y √2, tienen decimales infinitos no periódicos porque no pueden escribirse como fracción de enteros.",
          "misconception_tag": null
        },
        "periodic_as_irrational": {
          "title": "⚠ No todo decimal infinito es irracional",
          "body": "0.333… es infinito, pero repite el 3.\nComo:\n0.333… = 1/3\nes racional.",
          "misconception_tag": "cree_que_todo_decimal_infinito_es_irracional"
        },
        "integer_as_irrational": {
          "title": "⚠ Recuerda los enteros",
          "body": "7 es racional porque puede escribirse como:\n7 = 7/1\nTodo entero es racional.",
          "misconception_tag": "cree_que_enteros_no_son_racionales"
        },
        "irrational_as_rational": {
          "title": "⚠ Revisa la repetición",
          "body": "π y √2 tienen decimales infinitos no periódicos.\nNo pueden escribirse como fracción de enteros. Por eso son irracionales.",
          "misconception_tag": "no_reconoce_irracional_como_real"
        }
      }
    }
  },

  "events_to_register": [
    "node_viewed",
    "decimal_comparison_viewed",
    "interaction_attempt:I1_reconocer_periodico",
    "pi_example_viewed",
    "pausa_aproximacion_viewed",
    "interaction_attempt:I2_aproximacion_vs_exacto",
    "formalization_viewed",
    "notation_note_viewed",
    "optional_branch_decision",
    "optional_branch_taken",
    "interaction_attempt:I_OPT_sqrt2_exacto",
    "misconception_detected",
    "feedback_viewed",
    "mini_challenge_attempt",
    "mini_challenge_result",
    "node_completed",
    "transition_initiated"
  ],

  "alert_conditions": [
    {
      "condition_id": "ALERT_OBSERVATION_INFINITE_AS_IRRATIONAL",
      "level": "observation",
      "trigger": "Student classifies 0.333… as irrational but corrects after feedback",
      "message_educator": "El estudiante inicialmente clasificó un decimal periódico como irracional, pero corrigió después de la retroalimentación. Se recomienda observar si esta dificultad reaparece."
    },
    {
      "condition_id": "ALERT_REINFORCEMENT_APPROXIMATION",
      "level": "reinforcement_suggested",
      "trigger": "Student confuses approximation with exact value two or more times",
      "message_educator": "El estudiante presenta dificultad recurrente para distinguir aproximaciones de valores exactos. Se recomienda reforzar la idea de que ninguna cantidad finita de decimales iguala a un irracional."
    },
    {
      "condition_id": "ALERT_INTERVENTION_IRRATIONAL_CONCEPT",
      "level": "teacher_intervention",
      "trigger": "Student persists in misclassifying rationals/irracionales after viewing formalization and feedback",
      "message_educator": "El estudiante mantiene dificultades para diferenciar racionales de irracionales. Se recomienda intervención directa enfatizando el criterio 'no se puede escribir como fracción'."
    },
    {
      "condition_id": "ALERT_GROUP_INFINITE_DECIMAL",
      "level": "observation_group",
      "trigger": "More than 40% of group classifies 0.333… as irrational",
      "message_educator": "Una proporción importante del grupo confunde decimal infinito con irracional. Puede ser útil reforzar colectivamente la distinción periódico/no-periódico."
    }
  ],

  "level_presentation": {
    "basico": {
      "comparison_table_detail": "with_per_row_explanation",
      "pi_example_detail": "developed",
      "optional_branch": "recommended_with_visual",
      "default_expanded": true,
      "hint_availability": "máximo"
    },
    "intermedio": {
      "comparison_table_detail": "standard",
      "pi_example_detail": "standard",
      "optional_branch": "available",
      "default_expanded": false,
      "hint_availability": "medio"
    },
    "avanzado": {
      "comparison_table_detail": "compact",
      "pi_example_detail": "brief",
      "optional_branch": "recommended_as_extension",
      "default_expanded": false,
      "hint_availability": "mínimo",
      "challenge_variant": "includes √4 (=2, racional), 0.101001000…, φ"
    }
  },

  "design_handoff": {
    "node_state": "bloqueado|actual|completado",
    "path_position": "ruta_nucleo_fourth_numeric_set",
    "optional_branch_visual": "puntico opcional-explorable ramificado",
    "components_required": [
      "[componente-katia-dialogo]",
      "[componente-tabla-comparativa-decimales]",
      "[componente-pregunta-opcion-unica]",
      "[componente-decimal-infinito-animado]",
      "[componente-aproximacion-vs-exacto]",
      "[componente-camino-opcional]",
      "[componente-cuadrado-diagonal]",
      "[componente-mini-reto-clasificacion]",
      "[componente-retroalimentacion-modal]",
      "[componente-formalización-expandible]",
      "[componente-ejemplos-tarjetas]",
      "[componente-transicion-hexagono]"
    ],
    "design_tokens": [
      "[asset-mascota:Katia]",
      "[color-acento-morado]",
      "[color-acento-teal]",
      "[tipografia-titulo]",
      "[tipografia-body]"
    ],
    "render_blocker": "Verificar render de: π, √2, √3, √4, e, 0.25, 0.333…, 3.14, 3.14159265…, 1.41421356…, 1/4, 1/3, 7/1, ∈, ∉, R, Q, I, Q'"
  }
}
```

---

## Notas finales

Este documento preserva **todo el guión íntegro** de B07, incluyendo:
- ✅ Texto completo de Katia
- ✅ Tabla comparativa de tres tipos de decimales
- ✅ Las 2 interacciones principales + 1 interacción opcional (√2)
- ✅ Ejemplo de π + pausa aproximación/exacto
- ✅ **Camino opcional de √2** (gating suave, no bloquea progreso)
- ✅ Nota sobre notación (I vs i)
- ✅ Mini reto de clasificación racional/irracional
- ✅ Storyboard detallado
- ✅ JSON técnico limpio

**Corrección clave aplicada:** La definición de irracional se ancla en **"no se puede escribir como fracción de enteros"** (criterio estructural), con el comportamiento decimal como consecuencia. Esto está marcado explícitamente en la formalización y en las notas pedagógicas.

Sigue el mismo calibre que B04, B05 y B06.
