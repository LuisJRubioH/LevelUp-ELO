# Nodo: El exponente cuenta factores, no sumandos — PREALG-N2-E05-POTENCIACION-CRECER

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `PREALG-N2-E05-POTENCIACION-CRECER` |
| `concept_slug` | `potenciacion` |
| Error focal | `potencia_es_multiplicar_por_el_exponente` |
| Sala / edificio | El Invernadero |
| Guía | KatIA |
| Entra después de | `PREALG-N2-E00-CIUDAD` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El Invernadero · Potenciación

**Título:** El exponente cuenta factores, no sumandos

Aquí dentro nada crece sumando: cada día multiplica al anterior. Vas a ver qué dice exactamente el número pequeño de arriba, por qué 2³ no es 6, y hasta dónde llega esta operación cuando el exponente deja de ser un número de contar.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar al invernadero. Sin nota.

**D1**

¿Cuánto vale $2^{3}$?

Respuesta: `8`

**D2**

¿Qué significa $5^{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `factor` | 5 multiplicado por sí mismo 2 veces | — |
| 　 | `sum` | 5 sumado 2 veces | `potencia_es_suma_repetida` |
| 　 | `product` | 5 multiplicado por 2 | `potencia_es_multiplicar_por_el_exponente` |

**D3**

Un esqueje se duplica cada día. Si hoy hay 1, ¿cuántos habrá en 4 días?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sixteen` | 16 | — |
| 　 | `eight` | 8 | `cuenta_mal_los_pasos` |
| 　 | `four` | 4 | `crecimiento_lineal` |
| 　 | `two_four` | 2 × 4 = 8 | `potencia_es_multiplicar_por_el_exponente` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · Dentro del Invernadero* — **El esqueje que se comió la bandeja**

El quinto edificio es el Invernadero: techo de vidrio, bandejas de germinación en filas y un registro colgado en la puerta donde el jardinero anota cada mañana cuántos esquejes hay. La variedad que cultivan tiene una particularidad — cada día se duplica sola.

El aprendiz calculó el encargo así: «Un esqueje que se duplica durante 10 días son 2 por 10, o sea 20 esquejes. Cabe de sobra en una bandeja». Pidió una bandeja. Al décimo día tuvieron que abrir un ala nueva del invernadero.

**Pregunta:** Un esqueje que se duplica cada día, ¿cuántos son al décimo día?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | 20: es 2 por 10 días | — |
| 　 | `b` | Unos cientos | — |
| 　 | `c` | Más de mil | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos registros del invernadero, dos crecimientos**

Las dos bandejas de abajo arrancan igual y crecen distinto. Mira cuánto aporta cada día en cada una.

- **Caso que ya conoces** — Cada día aporta lo mismo: 2. Es multiplicación.
- **Caso que rompe la expectativa** — Cada día aporta tanto como TODO lo acumulado. Es potenciación.

**Resolución:** 1024 contra 20: la diferencia no es que un número sea más grande, es que las dos operaciones cuentan cosas distintas. En la multiplicación el 10 cuenta SUMANDOS iguales; en la potencia el 10 cuenta FACTORES iguales. El aprendiz leyó el exponente como si fuera un factor, y se equivocó por más de mil.

**Definición — La potenciación**

$$a^{n}=\underbrace{a\times a\times\cdots\times a}_{n\ \text{factores}}$$

Elevar a a la n es multiplicar a por sí mismo n veces. La base dice qué se repite; el exponente dice cuántas veces se repite como FACTOR. No es a por n.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a` | base | el número que se repite |
| `n` | exponente | cuántas veces aparece la base como factor |
| `a^{n}` | potencia | el resultado |
| `a^{1}=a` | exponente uno | un solo factor: la base tal cual |
| `a^{0}=1` | exponente cero | ningún factor; el producto vacío es 1, no 0 |
| `a^{-n}=\dfrac{1}{a^{n}}` | exponente negativo | invierte la potencia; se sale de ℤ y cae en ℚ |

### A5. Ejemplos resueltos

#### Los diez días de la bandeja B · *resuelto*

Un esqueje que se duplica cada día. ¿Cuántos hay al décimo día, y por qué no cabía en una bandeja?

- Día 1: 2. Día 2: 2 × 2 = 4. Día 3: 4 × 2 = 8. Cada día multiplico por 2, no sumo 2.
- Al día n hay 2 multiplicado por sí mismo n veces: 2ⁿ.
- 2¹⁰ = 2×2×2×2×2×2×2×2×2×2. Lo agrupo: 2⁵ = 32, y 2¹⁰ = 32 × 32.
- 32 × 32 = 1024.
- 1024 esquejes, no 20. El aprendiz confundió el exponente con un factor.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': 'En el paso 3 se parte 2¹⁰ en 2⁵ × 2⁵. ¿Por qué se pueden juntar así los exponentes?'}

#### Cuando el exponente apunta al otro lado · *resuelto*

El registro del invernadero anota hacia atrás: si hoy hay 1 esqueje, ¿cuánto había 3 días antes, cuando aún se duplicaba cada día?

- Ir hacia adelante multiplica por 2; ir hacia atrás hace lo contrario: divide entre 2.
- Tres días atrás es dividir tres veces entre 2, y eso se escribe 2⁻³.
- 2⁻³ = 1 ÷ 2³ = 1/8.
- 1/8 = 0,125: un octavo de esqueje. No es un esqueje real, pero sí un número.
- El exponente negativo no da un número negativo: da el inverso. Y ese inverso ya no es entero.

#### El aprendiz que multiplicó la base por el exponente · *TRAMPA*

El aprendiz pide material así: «Necesito 3⁴ macetas. Eso es 3 por 4, o sea 12 macetas».

- Desarrolla la potencia sin atajos: 3 × 3 × 3 × 3.
- 3 × 3 = 9, 9 × 3 = 27, 27 × 3 = 81.
- 81 macetas, casi siete veces más de lo que pidió. La confusión cuesta caro cuando el exponente crece.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': '3^{4}=12', 'right_latex': '3^{4}=81', 'rows': [{'wrong': 'El exponente es un factor más', 'right': 'El exponente cuenta cuántas veces aparece la base'}, {'wrong': '3⁴ = 3 × 4', 'right': '3⁴ = 3 × 3 × 3 × 3'}]}
**¿Por qué falla?:** ¿Por qué 12 no puede ser la respuesta? Escribe la potencia desarrollada y su valor.


### A6. Puente — parcialmente resueltos

El procedimiento ya va empezado; completa los huecos.

**P1** (*falta: last*) — Una bandeja del invernadero tiene 4 filas de 4 macetas, y hay 4 bandejas iguales.

- dado: $4^{3}=4\times 4\times 4$
- dado: $4\times 4=16$
- hueco `P1-b1`: $4^{3}=$ → `64`

**P2** (*falta: middle*) — El registro cuenta hacia atrás dos días desde 1 esqueje.

- dado: $2^{-2}=\dfrac{1}{2^{2}}$
- hueco `P2-b1`: $2^{2}=$ → `4`
- hueco `P2-b2`: $2^{-2}\text{ en decimal}=$ → `0,25`

**P3** (*falta: statement_only*) — Solo el planteamiento: un esqueje que se TRIPLICA cada día, empezando por uno. ¿Cuántos hay al quinto día?

- hueco `P3-b1`: $3^{5}=$ → `243`


### A7. Comparación de métodos

**Dos caminos para la misma potencia**

¿Cuánto vale $2^{12}$? Las dos soluciones de abajo son correctas.

- **Método 1 · Multiplicar doce veces** — 
- **Método 2 · Partir el exponente** — 

**Pregunta:** ¿Cuál usarías para 2²⁰? ¿Y qué regla estás usando sin nombrarla en el método 2?

**Insight:** El método 2 usa que al multiplicar potencias de la misma base los exponentes se SUMAN: 2⁶ × 2⁶ = 2⁶⁺⁶ = 2¹². Tiene sentido si vuelves a la definición — seis factores junto a otros seis factores son doce factores. No es una regla que haya que memorizar: se lee en el conteo.

### A8. Práctica independiente (7 ítems)

**E1**

Una bandeja cuadrada tiene 6 filas de 6 macetas. ¿Cuántas macetas caben?

Respuesta: `36`

Escalera de pistas:
1. El exponente 2 dice cuántas veces aparece el 6 como factor.
2. 6 × 6.
3. 6 × 6 = 36, no 6 × 2.

**E2**

Un esqueje se duplica cada día. Si hoy hay 1, ¿cuántos habrá en 6 días?

Respuesta: `64`

Escalera de pistas:
1. Cada día multiplica por 2, no suma 2.
2. 2, 4, 8, 16…
3. 2⁵ = 32, y falta un día más.

**E3**

El registro cuenta hacia atrás: ¿cuánto vale $2^{-2}$? (decimal)

Respuesta: `0,25`

Escalera de pistas:
1. El exponente negativo invierte, no cambia el signo.
2. 2⁻² = 1 ÷ 2².
3. 1 ÷ 4 = …

**E4**

El aprendiz anota «$4^{3}=12$». ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `times` | Multiplicó la base por el exponente; lo correcto es 64 | — |
| 　 | `sum` | Sumó 4 tres veces | `potencia_es_suma_repetida` |
| 　 | `swapped` | Cambió base y exponente: quiso decir 3⁴ | `confunde_base_con_exponente` |
| 　 | `none` | Ningún error, está bien | `potencia_es_multiplicar_por_el_exponente` |

Escalera de pistas:
1. Desarrolla la potencia antes de juzgar.
2. 4³ = 4 × 4 × 4.
3. 4 × 4 = 16, y 16 × 4 = 64.

**E5**

¿Es verdadera o falsa? «Para todo $a$ y todo $n$: $a^{n}=a\times n$.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false_factors` | Falsa: el exponente cuenta factores, no es un factor | — |
| 　 | `true` | Verdadera: elevar es multiplicar por el exponente | `potencia_es_multiplicar_por_el_exponente` |
| 　 | `false_never` | Falsa: nunca coinciden los dos resultados | `olvida_el_caso_de_igualdad` |
| 　 | `true_small` | Verdadera si los números son pequeños | `potencia_es_multiplicar_por_el_exponente` |

Escalera de pistas:
1. Para tumbar un «para todo» basta UN caso.
2. Prueba con a = 3 y n = 4.
3. 3⁴ = 81 y 3 × 4 = 12. ¿Hay algún par donde sí coincidan? Prueba a = 2, n = 2.

**E6**

Un esqueje se triplica cada día. Si hoy hay 1, ¿cuántos habrá al cuarto día?

Respuesta: `81`

Escalera de pistas:
1. Triplicarse es multiplicar por 3 cada día.
2. 3 × 3 = 9.
3. 9 × 3 = 27, y falta un día.

**E7**

¿Cuál de estas potencias de base y exponente enteros SE SALE de los enteros?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `neg_exp` | 2 elevado a -1 | — |
| 　 | `zero_exp` | 7 elevado a 0 | `exponente_cero_da_cero` |
| 　 | `neg_base` | -3 elevado a 2 | `base_negativa_da_no_entero` |
| 　 | `big` | 5 elevado a 4 | `confunde_grande_con_fuera_del_conjunto` |

Escalera de pistas:
1. Calcula las cuatro y mira cuál no es un entero.
2. 7⁰ = 1 y (−3)² = 9: los dos son enteros.
3. 2⁻¹ = 1/2, que es racional pero no entero.


### A9. Cierre

*La escalera de la potenciación* — **¿La potencia de dos elementos del conjunto vive en el conjunto?**

Esta operación rompe DOS peldaños, y el segundo abre la puerta del nodo siguiente.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Multiplicar naturales por sí mismos da naturales, por grande que sea. |
|  | ✗ | El exponente negativo invierte, y el inverso de un entero casi nunca es entero. |
|  | ✗ | Con exponente fraccionario la potencia se sale de ℚ. Este es el hueco del que sale la Cantera (E06). |
|  | ✗ | Ni siquiera con exponente natural: el resultado SE SALE. Ninguna operación aritmética cierra 𝕀. |
|  | ~ (ámbar) | Cierra con base positiva (π² ∈ ℝ). Se rompe en un solo caso: base negativa con exponente fraccionario, y ahí empieza B09. |
|  | ✅ | El único peldaño donde toda potencia tiene respuesta. Desvío opcional (B09). |

El agujero de ℚ es el más interesante: 2^(1/2) existe, no es ninguna fracción, y ya lo conociste como √2 en B07. La operación que lo desentierra se llama radicación, y se trabaja en la Cantera.

#### Pregunta de abstracción

¿Qué comparten los tres casos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `factors` | En los tres el exponente dice cuántas veces aparece la base como factor | — |
| 　 | `bigger` | En los tres el resultado es mayor que la base | — |
| 　 | `repeated` | En los tres se repite una misma multiplicación | — |
| 　 | `base_two` | En los tres la base es 2 | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos esquejes hay al octavo día?
¿Cuántos esquejes hay al octavo día?

Respuesta: `256`

Escalera de pistas:
1. Duplicarse cada día durante 8 días es 2⁸.
2. Parte el exponente: 2⁸ = 2⁴ × 2⁴.
3. 2⁴ = 16, y 16 × 16 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otros números. Sin nota.

- **Mejoró:** Avance: ya lees el exponente como un contador de factores.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la diferencia entre el exponente y un factor.

**PD1**

¿Cuánto vale $3^{3}$?

Respuesta: `27`

**PD2**

¿Qué significa $6^{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `factor` | 6 multiplicado por sí mismo 2 veces | — |
| 　 | `product` | 6 multiplicado por 2 | `potencia_es_multiplicar_por_el_exponente` |
| 　 | `sum` | 6 sumado 2 veces | `potencia_es_suma_repetida` |

**PD3**

¿Es verdadera? $2^{2}=2\times 2$

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `true` | Verdadera | — |
| 　 | `false` | Falsa | `sobregeneraliza_potenciacion` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `PREALG-N2-E05-POTENCIACION-CRECER-D2` | `sum` | `potencia_es_suma_repetida` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-D2` | `product` | `potencia_es_multiplicar_por_el_exponente` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-D3` | `eight` | `cuenta_mal_los_pasos` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-D3` | `four` | `crecimiento_lineal` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-D3` | `two_four` | `potencia_es_multiplicar_por_el_exponente` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E4` | `sum` | `potencia_es_suma_repetida` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E4` | `swapped` | `confunde_base_con_exponente` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E4` | `none` | `potencia_es_multiplicar_por_el_exponente` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E5` | `true` | `potencia_es_multiplicar_por_el_exponente` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E5` | `false_never` | `olvida_el_caso_de_igualdad` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E5` | `true_small` | `potencia_es_multiplicar_por_el_exponente` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E7` | `zero_exp` | `exponente_cero_da_cero` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E7` | `neg_base` | `base_negativa_da_no_entero` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-E7` | `big` | `confunde_grande_con_fuera_del_conjunto` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-PD2` | `product` | `potencia_es_multiplicar_por_el_exponente` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-PD2` | `sum` | `potencia_es_suma_repetida` | Desarrolla la potencia como producto antes de responder. |
| `PREALG-N2-E05-POTENCIACION-CRECER-PD3` | `false` | `sobregeneraliza_potenciacion` | Desarrolla la potencia como producto antes de responder. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `/leccion/02-prealg-n2-mercado/e05-potenciacion-katia-v4.png`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
