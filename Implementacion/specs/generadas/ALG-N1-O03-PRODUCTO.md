# Nodo: Multiplicar potencias es contar factores, no amontonar exponentes — ALG-N1-O03-PRODUCTO

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N1-O03-PRODUCTO` |
| `concept_slug` | `producto_de_monomios` |
| Error focal | `multiplica_los_exponentes_al_multiplicar` |
| Sala / edificio | El taller de cinceles |
| Guía | Bakenra |
| Entra después de | `ALG-N1-O02-SIGNOS` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El taller de cinceles · Producto de monomios

**Título:** Multiplicar potencias es contar factores, no amontonar exponentes

En el patio aprendiste que un signo de fuera entra hasta el último término. Aquí lo de fuera no es un signo, es un factor — y cuando las letras se multiplican entre sí hay una contabilidad nueva que llevar: la de los exponentes.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de entrar al taller. Sin nota.

**D1**

¿Cuánto es 2³?

Respuesta: `8`

**D2**

¿Cuánto es 4 · (2 + 3)?

Respuesta: `20`

**D3**

¿A qué equivale $x^{2}\cdot x^{3}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `five` | $x^{5}$ | — |
| 　 | `six` | $x^{6}$ | `multiplica_los_exponentes_al_multiplicar` |
| 　 | `two` | $2x^{5}$ | `suma_las_bases_al_multiplicar` |

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el taller de cinceles* — **El pedido de piedra que no cabía en Egipto**

En el taller se afilan las hojas y se marcan las plantillas de cada sillar. Bakenra tiene delante un pedido de piedra que le llegó del tallador mayor.

«Para una hilada hacen falta x² sillares, y hay que levantar x³ hiladas. El tallador pidió x⁶ sillares. Con x = 10 eso es un millón de piedras.»

Bakenra deja la tablilla sobre el banco.

«La cantera entera ha sacado ochenta mil piedras en veinte años. El número estaba mal, y lo peor es que sabía la regla: la dijo en voz alta antes de escribirla.»

**Pregunta:** Al multiplicar dos potencias de la misma letra, ¿qué pasa con los exponentes?

**Intento genuino** (`acotado`): Escoge lo que creas ahora. No se califica.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `a` | Se multiplican entre sí, igual que las potencias | — |
| 　 | `b` | Se suman | — |
| 　 | `c` | Se queda el mayor de los dos | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Desplegar la potencia y contar**

Una potencia es una abreviatura. Si se despliega, no hay nada que recordar.

- **Multiplicar potencias** — Dos factores y tres factores son cinco factores. Los exponentes se SUMAN.
- **Elevar una potencia** — Tres grupos de dos factores son seis. Aquí sí se multiplican los exponentes.

**Resolución:** Las dos reglas salen de lo mismo: contar cuántas veces está escrita la letra. Multiplicar dos potencias junta los factores de las dos, así que se suman los exponentes. Elevar una potencia repite el grupo entero, así que se multiplican. El error del tallador fue usar la segunda cuenta para el primer caso.

**Definición — Producto de monomios**

$$(a x^{m})(b x^{n}) = ab\,x^{m+n}$$

Para MULTIPLICAR dos monomios se multiplican los coeficientes y, en cada letra que aparezca en los dos, se SUMAN los exponentes. Las letras que solo aparecen en uno se copian tal cual. Cuidado con lo que no se mezcla: los coeficientes se multiplican, los exponentes se suman — cada uno lleva su propia cuenta.

| Símbolo | Se lee | Significa |
|---|---|---|
| `x^{2}\cdot x^{3}=x^{5}` | equis dos por equis tres | misma letra: se suman los exponentes |
| `(3x)(4x)=12x^{2}` | tres equis por cuatro equis | coeficientes se multiplican, exponentes se suman |
| `x=x^{1}` | el exponente invisible | una letra sola lleva un 1 que no se escribe |
| `x^{2}\cdot y^{3}` | no se junta | letras distintas: no hay nada que sumar |
| `(x^{2})^{3}=x^{6}` | potencia de potencia | el otro caso: aquí SÍ se multiplican |

### A5. Ejemplos resueltos

#### Repartir un factor por dentro del paréntesis · *resuelto*

Cada plantilla del taller marca (2f + 3) trazos, donde f son los filos que lleva la hoja. Hay que marcar 4 plantillas iguales. ¿Cuántos trazos son?

- El 4 multiplica a la plantilla ENTERA, igual que el menos del patio afectaba a todo.
- Reparto el 4 a cada término: 4 · 2f y 4 · 3.
- 4 · 2f = 8f, porque se multiplican los coeficientes y la f se copia.
- 4 · 3 = 12.
- Quedan 8f + 12. Con f = 5: 4 · 13 = 52, y 8 · 5 + 12 = 52 ✓.

**Autoexplicación (focal):** {'step_index': 2, 'prompt': '¿Por qué el 4 multiplica también al 3, si el 3 no tiene letra?'}

#### Multiplicar dos monomios · *resuelto*

Cada hilada lleva 3s sillares y hay que levantar 5s² hiladas, donde s es el ancho del muro en varas. ¿Cuántos sillares hacen falta?

- Separo las dos cuentas: la de los coeficientes y la de la letra.
- Coeficientes: 3 · 5 = 15. Se multiplican, como cualquier par de números.
- Letra: s es s¹, así que s¹ · s² tiene 1 + 2 = 3 factores → s³.
- Junto las dos cuentas: 15s³.
- Compruebo con s = 2: (6)(20) = 120, y 15 · 8 = 120 ✓.

#### El tallador que multiplicó los exponentes · *TRAMPA*

Vuelve el pedido de la apertura: x² sillares por hilada, x³ hiladas. El tallador escribió x²·x³ = x⁶ y pidió un millón de piedras.

- Escribo la x tantas veces como diga cada exponente: x·x y x·x·x.
- Las junto todas en fila y cuento: cinco. No hay manera de que salgan seis.
- Regla para no volver a caer: si dudas, despliega y cuenta. La regla es el atajo, no la fuente.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': 'x^{2}\\cdot x^{3}=x^{2\\cdot 3}=x^{6}', 'right_latex': 'x^{2}\\cdot x^{3}=x^{2+3}=x^{5}', 'rows': [{'wrong': 'Multiplicar potencias multiplica los exponentes', 'right': 'Multiplicar potencias junta los factores: se suman'}, {'wrong': '(x\\cdot x)(x\\cdot x\\cdot x)\\ \\text{tiene}\\ 6\\ \\text{factores}', 'right': '(x\\cdot x)(x\\cdot x\\cdot x)\\ \\text{tiene}\\ 5\\ \\text{factores}'}]}
**¿Por qué falla?:** Despliega los dos productos y di cuántas veces aparece la x. Después explica en qué caso sí se multiplican los exponentes.


### A6. Puente — parcialmente resueltos

El pedido va empezado; completa los huecos.

**P1** (*falta: last*) — Multiplica $(2f)(6f)$.

- dado: $2\cdot 6=12$
- dado: $f^{1}\cdot f^{1}=f^{2}$
- hueco `P1-b1`: $\text{coeficiente del resultado}=$ → `12`

**P2** (*falta: middle*) — Reparte el factor: $5(3s+4)$, y evalúa con $s=2$.

- dado: $5\cdot 3s+5\cdot 4$
- hueco `P2-b1`: $5\cdot 4=$ → `20`
- hueco `P2-b2`: $15\cdot 2+20=$ → `50`

**P3** (*falta: statement_only*) — Solo el planteamiento: $(4s^{2})(3s)$ con $s=2$. Primero el monomio, después el valor.

- hueco `P3-b1`: $12s^{3}\ \text{con}\ s=2:$ → `96`


### A7. Comparación de métodos

**Dos maneras de multiplicar potencias**

$x^{3}\cdot x^{4}$. Las dos llegan al mismo sitio; una sabe por qué.

- **Método 1 · Aplicar la regla** — 
- **Método 2 · Desplegar y contar** — 

**Pregunta:** ¿Cuál de los dos te avisa de que $(x^{3})^{4}$ NO es $x^{7}$?

**Insight:** El segundo. Desplegar (x³)⁴ da cuatro grupos de tres factores, doce en total, y el error se ve antes de cometerlo. El primero no avisa de nada: si has guardado la regla equivocada, la aplica igual de rápido. Por eso conviene desplegar mientras la mano no lo tenga automático — y volver a desplegar el día que dudes, en vez de escoger la regla que suene mejor.

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuánto es $(3x^{2})(4x^{3})$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $12x^{5}$ | — |
| 　 | `trap` | $12x^{6}$ | `multiplica_los_exponentes_al_multiplicar` |
| 　 | `sumcoef` | $7x^{5}$ | `suma_los_coeficientes_al_multiplicar` |
| 　 | `keep` | $12x^{3}$ | `se_queda_el_mayor_exponente` |

Escalera de pistas:
1. Lleva dos cuentas separadas: coeficientes y exponentes.
2. Los coeficientes se multiplican: 3 · 4.
3. Los exponentes se suman: 2 + 3.

**E2**

Reparte el factor en $6(2f+5)$ y escribe el resultado. No dejes espacios.

Respuesta: `12f+30`
También válidas: `30+12f`

Escalera de pistas:
1. El 6 multiplica a los dos términos.
2. 6 · 2f = 12f.
3. 6 · 5 = 30.

**E3**

Cada hilada lleva $2s$ sillares y hay $4s$ hiladas. Con $s=3$, ¿cuántos sillares hacen falta en total?

Respuesta: `72`

Escalera de pistas:
1. Primero el monomio: 2 · 4 = 8 y s · s = s².
2. Queda 8s².
3. 8 · 9 = …

**E4**

Un tallador escribe $(2x)(5x^{4})=10x^{4}$. ¿Dónde está el error?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `exp` | Olvidó que $x$ es $x^{1}$: el exponente es $1+4=5$ | — |
| 　 | `coef` | Multiplicó mal los coeficientes | `suma_los_coeficientes_al_multiplicar` |
| 　 | `mult` | Debió multiplicar los exponentes: $x^{4}$ | `multiplica_los_exponentes_al_multiplicar` |
| 　 | `none` | No hay error | `olvida_el_exponente_invisible` |

Escalera de pistas:
1. Los coeficientes están bien: 2 · 5 = 10.
2. ¿Qué exponente tiene una x escrita sola?
3. Despliega: (x)(x·x·x·x) son cinco factores.

**E5**

¿Verdadera o falsa? «Al multiplicar dos potencias de la misma letra, los exponentes se multiplican.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: se suman — $x^{2}\cdot x^{3}=x^{5}$, no $x^{6}$ | — |
| 　 | `true` | Verdadera: si las potencias se multiplican, sus exponentes también | `multiplica_los_exponentes_al_multiplicar` |
| 　 | `true_same` | Verdadera cuando los dos exponentes son iguales | `multiplica_los_exponentes_al_multiplicar` |
| 　 | `false_never` | Falsa: los exponentes nunca se multiplican en ningún caso | `sobregeneraliza_producto_de_monomios` |

Escalera de pistas:
1. Despliega x² · x³ y cuenta las x.
2. Son cinco factores, no seis.
3. Multiplicar exponentes es lo de (x²)³, que es otra cosa.

**E6**

Selecciona TODAS las igualdades verdaderas.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `a` | $x^{4}\cdot x^{2}=x^{6}$ | — |
| 　 | `b` | $x^{4}\cdot x^{2}=x^{8}$ | — |
| ✅ | `c` | $(x^{4})^{2}=x^{8}$ | — |
| 　 | `d` | $x^{4}+x^{2}=x^{6}$ | — |

Escalera de pistas:
1. Mira si la operación de fuera es un producto, una potencia o una suma.
2. Producto de potencias: se suman. Potencia de potencia: se multiplican.
3. En una SUMA no se toca ningún exponente.

**E7**

El taller marca $3(2f+7)$ trazos por plantilla y hay $2f$ plantillas. Con $f=1$, ¿cuántos trazos se marcan en total?

Respuesta: `54`

Escalera de pistas:
1. Primero reparte el 3: 6f + 21.
2. Con f = 1 son 27 trazos por plantilla.
3. Y hay 2 plantillas: 2 · 27 = …


### A9. Cierre

*¿Se suman los exponentes?* — **Cada operación lleva su propia cuenta**

«Se suman» no es la regla de los exponentes: es la regla de UNA operación. Fíjate en qué está pasando por fuera antes de tocar nada.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | Se juntan los factores de las dos: 2 + 3. Es el caso focal. |
|  | ✅ | Una letra sola es elevada a 1. El mismo caso, con un 1 que no se escribe. |
|  | ~ (ámbar) | Los exponentes sí se suman, pero los coeficientes NO: esos se multiplican. Dos cuentas a la vez. |
|  | ✗ | No hay exponentes que sumar: cada letra lleva su cuenta y el producto se deja indicado. |
|  | ✗ | Aquí se MULTIPLICAN: se repite tres veces un grupo de dos factores. |
|  | ✗ | No se toca ningún exponente. No son semejantes, así que la suma se queda indicada. |

La tercera fila es la que más se cobra en los exámenes: en un mismo monomio conviven dos cuentas distintas, y la mano tiende a aplicarle a los coeficientes lo que acaba de hacer con los exponentes. La última recuerda que una suma no es un producto — 3x² y 4x³ ni se suman ni se juntan.

#### Pregunta de abstracción

¿Qué comparten los tres pedidos trabajados en este nodo?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `count` | En los tres el resultado se puede comprobar desplegando y contando | — |
| 　 | `two_books` | En los tres hay que llevar por separado la cuenta de los números y la de las letras | — |
| 　 | `same_rule` | En los tres se aplica la misma cuenta a los coeficientes y a los exponentes | — |
| 　 | `always_add` | En los tres los exponentes siempre se suman | — |

#### Ítem final con protocolo de Pólya

**CIERRE**

¿Cuántos sillares hay que tallar?
¿Cuántos sillares hay que tallar?

Respuesta: `48`

Escalera de pistas:
1. Multiplica coeficientes y suma exponentes.
2. Queda 6h³.
3. 6 · 2³ = 6 · 8 = …

Pólya: comprender → planear → ejecutar → comprobar


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres de la entrada, con otras piezas. Sin nota.

- **Mejoró:** Avance: ya distingues el producto de potencias de la potencia de una potencia.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo el despliegue: escribir la letra tantas veces como diga el exponente y contar.

**PD1**

¿Cuánto es 3³?

Respuesta: `27`

**PD2**

¿Cuánto es 6 · (4 + 2)?

Respuesta: `36`

**PD3**

¿A qué equivale $y^{4}\cdot y^{2}$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `six` | $y^{6}$ | — |
| 　 | `eight` | $y^{8}$ | `multiplica_los_exponentes_al_multiplicar` |
| 　 | `two` | $2y^{6}$ | `suma_las_bases_al_multiplicar` |

**Footer:** Estado de dominio — Un ítem resuelto con pista 2 o 3 queda en consolidación, y lo decimos.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N1-O03-PRODUCTO-D3` | `six` | `multiplica_los_exponentes_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-D3` | `two` | `suma_las_bases_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E1` | `trap` | `multiplica_los_exponentes_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E1` | `sumcoef` | `suma_los_coeficientes_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E1` | `keep` | `se_queda_el_mayor_exponente` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E4` | `coef` | `suma_los_coeficientes_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E4` | `mult` | `multiplica_los_exponentes_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E4` | `none` | `olvida_el_exponente_invisible` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E5` | `true` | `multiplica_los_exponentes_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E5` | `true_same` | `multiplica_los_exponentes_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-E5` | `false_never` | `sobregeneraliza_producto_de_monomios` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-PD3` | `eight` | `multiplica_los_exponentes_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |
| `ALG-N1-O03-PRODUCTO-PD3` | `two` | `suma_las_bases_al_multiplicar` | Si dudas, despliega la potencia y cuenta cuántas veces aparece la letra. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
