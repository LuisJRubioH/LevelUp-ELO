# Nodo: Hay una huella que no está en el catálogo, y no es que falte — ALG-N3-G02-CUADRADOS

*Generado desde el módulo por `scripts/generar_specs.py`. Editar el módulo, no este archivo — salvo los huecos marcados PENDIENTE.*

## A0. Ficha del nodo

| Campo | Valor |
|---|---|
| `node_id` | `ALG-N3-G02-CUADRADOS` |
| `concept_slug` | `diferencia_de_cuadrados_y_tcp` |
| Error focal | `suma_de_cuadrados_es_factorizable` |
| Sala / edificio | El cotejo de huellas |
| Guía | Salim |
| Entra después de | `ALG-N3-G01-FACTOR-COMUN` |
| Mueve ELO | no |
| Ítems: diagnóstico / práctica / post | 3 / 7 / 3 |

**Estándares (DBA / ICFES / grado) y tiempo estimado:**

> **PENDIENTE — se escribe a mano.** No es derivable del código.

---

## PARTE A — Especificación por bloques

### A1. Encabezado

**Kicker:** El cotejo de huellas · Diferencia de cuadrados y trinomio cuadrado perfecto

**Título:** Hay una huella que no está en el catálogo, y no es que falte

En el pesaje abrías fardos por lo que compartían sus bultos. Aquí llegan fardos que no comparten nada y aun así se abren: llevan la marca del troquel que los estampó. El oficio es cotejar la marca contra el catálogo. Y lo difícil no es reconocer las que están: es aceptar que una de las que buscas no existe.

**Escena:** — (nodo sin peldaño)

### A2. Mini-diagnóstico

Tres rápidas antes de abrir el catálogo. Sin nota.

**D1**

¿Cuál es la raíz cuadrada de 49?

Respuesta: `7`

**D2**

¿A qué equivale $(x+3)(x-3)$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `dif` | $x^{2}-9$ | — |
| 　 | `sum` | $x^{2}+9$ | `conjugado_da_suma_de_cuadrados` |
| 　 | `mid` | $x^{2}-6x+9$ | `confunde_conjugados_con_cuadrado_de_binomio` |

**D3**

En $x^{2}+6x+9$, ¿cuánto vale el doble producto de las raíces de los extremos?

Respuesta: `6`

*No corrige: es la línea base del post-diagnóstico.*

### A3. Apertura de KatIA — intento genuino

*KatIA · En el cotejo de huellas* — **La marca que el mozo se inventó**

En esta sala hay un catálogo de calcos: una hoja por cada troquel de la casa, con la huella que deja. Un fardo sin factor común se coteja contra el catálogo, y si su marca aparece, se sabe con qué troquel se cerró.

Salim abre el catálogo por la mitad:

«Llegó un fardo marcado $x^{2}+9$. El mozo vio dos cuadrados y buscó la hoja del cuño de la cenefa. Anotó que venía de $(x+3)(x-3)$ y lo mandó a desatar.»

«Ese cuño deja la marca $x^{2}-9$, con un menos. El fardo llegó cerrado y se fue roto: no venía de ningún troquel de esta casa.»

**Pregunta:** Si el cuño de la cenefa deja siempre una resta, ¿de qué troquel puede salir una suma de dos cuadrados?

**Intento genuino** (`acotado`): Escoge lo que más se acerque a lo que crees. Cualquiera vale.

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `ninguno` | De ninguno: esa huella no está en el catálogo | — |
| 　 | `mismo` | Del mismo, cambiando el signo al final | — |
| 　 | `otro` | De otro troquel que todavía no hemos visto | — |

### A4. Descubrimiento guiado + definición formal

*Descubrimiento guiado* — **Dos huellas en el catálogo, y un hueco**

Factorizar con troquel es leer al revés lo que aprendiste en la sala anterior. Cada estampa deja una marca reconocible.

- **Dos términos: la resta sí, la suma no** — Compruébalo: cualquier par de factores que pruebes deja un término del medio o cambia el signo. La suma de dos cuadrados no sale de multiplicar dos binomios.
- **Tres términos: hay que verificar el del medio** — No basta con que los extremos sean cuadrados: el del medio tiene que ser exactamente el doble producto de sus raíces.

**Resolución:** Dos huellas y un hueco. Con DOS términos: si restan y ambos son cuadrados, sale el cuño de la cenefa; si suman, no hay troquel. Con TRES términos: si los extremos son cuadrados Y el del medio es su doble producto, sale la matriz cuadrada; si el del medio no cuadra, tampoco hay troquel.

**Definición — Diferencia de cuadrados y trinomio cuadrado perfecto**

$$a^{2}-b^{2} = (a+b)(a-b) \qquad a^{2}\pm 2ab+b^{2} = (a\pm b)^{2}$$

DIFERENCIA DE CUADRADOS: dos términos, ambos cuadrados exactos, restando. Se abre como suma por diferencia de sus raíces. La SUMA de cuadrados no se factoriza.

TRINOMIO CUADRADO PERFECTO: tres términos; los extremos son cuadrados exactos y positivos, y el del medio es el doble producto de sus raíces. Se abre como el cuadrado de un binomio, con el signo del término del medio.

| Símbolo | Se lee | Significa |
|---|---|---|
| `a^{2}-b^{2}=(a+b)(a-b)` | a cuadrado menos b cuadrado, igual a a más b por a menos b | la huella del cuño de la cenefa, leída al revés |
| `a^{2}+b^{2}` | a cuadrado más b cuadrado | el hueco del catálogo: no sale de ningún troquel |
| `2ab` | dos a b | el doble producto, la condición que hay que verificar |
| `a^{2}-2ab+b^{2}=(a-b)^{2}` | a cuadrado menos dos a b más b cuadrado | los extremos siempre suman; el signo del medio va dentro del paréntesis |
| `x^{4}-16` | equis a la cuarta menos dieciséis | se abre, y uno de los trozos se vuelve a abrir |

### A5. Ejemplos resueltos

#### Restan y los dos son cuadrados · *resuelto*

Salim coteja un fardo marcado $4x^{2}-25$. ¿Se abre?

- Dos términos y restan: candidato a diferencia de cuadrados.
- ¿4x² es cuadrado exacto? Sí: (2x)². ¿25? Sí: 5².
- Las dos raíces son 2x y 5.
- Se abre como suma por diferencia: (2x + 5)(2x − 5).
- Compruebo estampando: (2x)² − 5² = 4x² − 25 ✓.

**Autoexplicación (focal):** {'step_index': 1, 'prompt': '¿Por qué hay que comprobar que los DOS términos son cuadrados exactos, y no basta con que uno lo sea?'}

#### El del medio decide · *resuelto*

Otro fardo: $4x^{2}+12xy+9y^{2}$. Los extremos prometen; falta comprobar el del medio.

- Extremos: 4x² = (2x)² y 9y² = (3y)². Los dos son cuadrados exactos y positivos.
- Raíces: 2x y 3y.
- Doble producto: 2 · 2x · 3y = 12xy.
- El trinomio tiene 12xy: coincide. Es cuadrado perfecto.
- El signo del medio es +, así que queda (2x + 3y)².

#### El mozo que abrió una suma de cuadrados · *TRAMPA*

Vuelve el fardo de la apertura. El mozo coteja $x^{2}+9$ contra la hoja del cuño y anota:

- (x + 3)(x − 3) = x² − 9. Deja un menos, no un más.
- Con x = 1: x² + 9 vale 10, y (x + 3)(x − 3) vale 4 · (−2) = −8.
- No solo son distintas: una es positiva y la otra negativa.
- Regla para no volver a caer: dos términos que SUMAN y son cuadrados → el fardo se devuelve cerrado.

**Confianza:** ¿Qué tan seguro estás de dónde falla?
**Versión correcta:** {'wrong_latex': 'x^{2}+9=(x+3)(x-3)', 'right_latex': 'x^{2}+9\\ \\text{no se factoriza}', 'rows': [{'wrong': 'Dos cuadrados, luego hay troquel', 'right': 'Dos cuadrados Y restando. La suma no tiene hoja en el catálogo'}, {'wrong': 'El signo del medio da igual', 'right': 'El signo es la marca: (x+3)(x−3) estampa x²−9, no x²+9'}]}
**¿Por qué falla?:** Estampa $(x+3)(x-3)$ y comprueba qué marca deja. Después prueba con $x=1$ en las dos expresiones y di cuánto se separan.


### A6. Puente — parcialmente resueltos

El cotejo va empezado; completa los huecos.

**P1** (*falta: last*) — Factoriza $9x^{2}-49$.

- dado: $\sqrt{9x^{2}}=3x$
- hueco `P1-b1`: $\sqrt{49}=$ → `7`

**P2** (*falta: middle*) — ¿Es $x^{2}+10x+25$ cuadrado perfecto?

- dado: $\sqrt{x^{2}}=x,\quad \sqrt{25}=5$
- hueco `P2-b1`: $2\cdot x\cdot 5\ \text{, coeficiente}=$ → `10`
- hueco `P2-b2`: $\text{términos del binomio resultante}=$ → `2`

**P3** (*falta: statement_only*) — Solo el planteamiento: $m^{2}-8m+25$. Comprueba las tres condiciones y di cuál falla.

- hueco `P3-b1`: $\text{doble producto que debería tener}=$ → `10`


### A7. Comparación de métodos

**Dos maneras de decidir si un fardo se abre**

$4x^{2}-4x+9$. Una tantea; la otra verifica.

- **Método 1 · Probar binomios** — 
- **Método 2 · Verificar el doble producto** — 

**Pregunta:** ¿Cuál de los dos sirve también cuando el fardo NO se abre?

**Insight:** El segundo. Probando binomios uno puede descartar dos candidatos y quedarse con la duda de si faltaba probar otro. Verificando el doble producto se obtiene una respuesta cerrada: o el término del medio es exactamente 2ab, o no es cuadrado perfecto, y no hay tercera opción. Por eso este método también contesta las preguntas que empiezan por «¿se puede…?».

### A8. Práctica independiente (7 ítems)

**E1**

¿Cuál es la factorización de $4x^{2}-25$?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `ok` | $(2x+5)(2x-5)$ | — |
| 　 | `sq` | $(2x-5)^{2}$ | `confunde_diferencia_con_cuadrado_perfecto` |
| 　 | `half` | $(4x+5)(x-5)$ | `no_saca_la_raiz_del_coeficiente` |
| 　 | `none` | No se puede factorizar | `suma_de_cuadrados_es_factorizable` |

Escalera de pistas:
1. Dos términos que restan: busca las raíces de cada uno.
2. √(4x²) = 2x y √25 = 5.
3. Suma por diferencia de esas dos raíces.

**E2**

¿Es $5a^{2}+30ab+9b^{2}$ un trinomio cuadrado perfecto?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no_first` | No: 5 no es cuadrado exacto, así que el primer término no tiene raíz | — |
| 　 | `yes` | Sí: $(5a+3b)^{2}$ | `no_saca_la_raiz_del_coeficiente` |
| 　 | `no_mid` | No: los extremos están bien, falla el del medio | `no_verifica_los_extremos_antes_del_medio` |
| 　 | `no_sign` | No: le falta un signo menos | `cree_que_el_signo_decide_el_tcp` |

Escalera de pistas:
1. La primera condición es que los extremos sean cuadrados exactos.
2. ¿Qué número al cuadrado da 5?
3. Ninguno entero: ni hace falta mirar el término del medio.

**E3**

¿Para qué valor POSITIVO de $k$ es $x^{2}+kx+36$ un trinomio cuadrado perfecto?

Respuesta: `12`

Escalera de pistas:
1. Los extremos son x² y 36; sus raíces son x y 6.
2. El del medio tiene que ser el doble producto de esas raíces.
3. 2 · 1 · 6.

**E4**

En $m^{2}-8m+25$ los extremos son cuadrados. ¿Cuánto tendría que valer el coeficiente del medio, sin signo, para que fuera cuadrado perfecto?

Respuesta: `10`

Escalera de pistas:
1. Las raíces de los extremos son m y 5.
2. El doble producto es 2 · m · 5.
3. Falla por poco: tiene 8 y necesitaría 10.

**E5**

Un mozo anota $x^{4}-16=(x^{2}+4)(x^{2}-4)$ y cierra el albarán. ¿Está terminado?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `no` | No: $x^{2}-4$ es otra diferencia de cuadrados y se vuelve a abrir | — |
| 　 | `yes` | Sí: ya está en dos factores | `factor_comun_incompleto` |
| 　 | `wrong` | No: el primer factor $x^{2}+4$ también se abre | `suma_de_cuadrados_es_factorizable` |
| 　 | `err` | No: la factorización está mal, debería ser $(x^{2}+4)^{2}$ | `confunde_diferencia_con_cuadrado_perfecto` |

Escalera de pistas:
1. La factorización es correcta. La pregunta es si está terminada.
2. Mira dentro de cada factor, como en el pesaje de entrada.
3. x² − 4 son dos cuadrados que restan.

**E6**

¿Verdadera o falsa? «Si una expresión tiene dos términos y los dos son cuadrados exactos, se puede factorizar.»

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `false` | Falsa: solo si RESTAN. Si suman, no hay troquel | — |
| 　 | `true` | Verdadera: dos cuadrados siempre dan suma por diferencia | `suma_de_cuadrados_es_factorizable` |
| 　 | `true_pos` | Verdadera, y el signo solo cambia el orden de los factores | `suma_de_cuadrados_es_factorizable` |
| 　 | `false_never` | Falsa: con dos términos nunca se puede factorizar | `cree_que_dos_terminos_nunca_se_factorizan` |

Escalera de pistas:
1. Prueba a estampar (x + 3)(x − 3) y mira qué signo deja.
2. Deja x² − 9.
3. Con x = 1, x² + 9 vale 10 y (x+3)(x−3) vale −8.

**E7**

Salim reparte cuatro fardos SIN abrirlos. ¿Cuáles se pueden abrir con las huellas de esta sala? Marca todas las que apliquen.

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `dif` | $9x^{2}-49$ | — |
| ✅ | `tcp` | $x^{2}+10x+25$ | — |
| 　 | `sum` | $x^{2}+49$ | `suma_de_cuadrados_es_factorizable` |
| 　 | `nomid` | $4x^{2}-4x+9$ | `no_verifica_el_doble_producto` |

Escalera de pistas:
1. Con dos términos: cuadrados exactos Y restando.
2. Con tres: extremos cuadrados Y el medio igual al doble producto.
3. En 4x² − 4x + 9 el doble producto sería 12x, no 4x. Son dos de los cuatro.


### A9. Cierre

*¿Está la huella en el catálogo?* — **Dos hojas, un hueco y un fardo que se abre dos veces**

El cotejo se decide mirando cuántos términos hay, si son cuadrados exactos y qué signo llevan. Esta es la hoja de ruta.

| Fila | ¿Cumple? | Nota |
|---|---|---|
|  | ✅ | La huella del cuño de la cenefa. Se abre siempre. |
|  | ✗ | El hueco del catálogo. No es que no lo hayamos visto todavía: no sale de multiplicar dos binomios. |
|  | ✅ | La huella de la matriz cuadrada. Los extremos siempre suman. |
|  | ✅ | El signo del medio es el que entra en el binomio; los extremos no cambian. |
|  | ✗ | Falla en la primera condición: ni hace falta mirar el término del medio. |
|  | ~ (ámbar) | Es diferencia de cuadrados, sí, pero uno de los trozos también lo es. Vale la regla del pesaje: mira dentro. El otro trozo, x² + 4, se queda cerrado. |

La regla en una línea: **la diferencia de cuadrados se abre; la suma, no.** Y con tres términos, los extremos son la entrada pero el que decide es el del medio.

#### Pregunta de abstracción

Los tres tienen dos cuadrados exactos. ¿Qué es lo único que decide si se abren?

| | id | Texto | Error que delata |
|---|---|---|---|
| 　 | `sign` | El signo y el número de términos: restando se abre, sumando no, y con tres decide el doble producto | — |
| 　 | `size` | El tamaño de los números: 9 es cuadrado y por eso los tres se abren | — |
| 　 | `letter` | Que aparezca la letra en los dos términos | — |

#### Ítem final con protocolo de Pólya

**C1**

¿Cuánto vale c?
¿Cuánto vale c?

Respuesta: `49`

Escalera de pistas:
1. El término del medio es el doble producto de las dos raíces.
2. Una raíz es x, así que 2 · x · b = 14x.
3. b = 7, y c es su cuadrado.

Pólya: Entender: el del medio es 14x y falta el último término. → Planear: el del medio es 2ab, con a = x. Despejo b y elevo al cuadrado. → Ejecutar: 2 · x · b = 14x → b = 7, así que c = 7² = 49. → Comprobar: x² + 14x + 49 = (x + 7)², y 2 · x · 7 = 14x ✓.


### A10. Post-diagnóstico y footer

Compara con: `diagnostic`

Las mismas tres, ahora que conoces el catálogo.

- **Mejoró:** Avance: ya distingues el fardo que se abre del que hay que devolver cerrado.
- **Igual:** Sin evidencia de avance todavía. KatIA va a retomar contigo la suma de cuadrados antes de seguir.

**Q1**

¿Cuál es la raíz cuadrada de 64?

Respuesta: `8`

**Q2**

¿Cuál de estas NO se puede factorizar?

| | id | Texto | Error que delata |
|---|---|---|---|
| ✅ | `sum` | $x^{2}+16$ | — |
| 　 | `dif` | $x^{2}-16$ | `suma_de_cuadrados_es_factorizable` |
| 　 | `tcp` | $x^{2}+8x+16$ | `no_verifica_el_doble_producto` |

**Q3**

En $x^{2}+12x+36$, ¿cuánto vale el doble producto de las raíces de los extremos?

Respuesta: `12`

**Footer:** Estado de la sala — Zona segura: nada de esto mueve tu ELO.

### A12. Misconceptions → feedback

| Interacción | Opción | Tag | Feedback |
|---|---|---|---|
| `ALG-N3-G02-CUADRADOS-D2` | `sum` | `conjugado_da_suma_de_cuadrados` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-D2` | `mid` | `confunde_conjugados_con_cuadrado_de_binomio` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E1` | `sq` | `confunde_diferencia_con_cuadrado_perfecto` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E1` | `half` | `no_saca_la_raiz_del_coeficiente` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E1` | `none` | `suma_de_cuadrados_es_factorizable` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E2` | `yes` | `no_saca_la_raiz_del_coeficiente` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E2` | `no_mid` | `no_verifica_los_extremos_antes_del_medio` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E2` | `no_sign` | `cree_que_el_signo_decide_el_tcp` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E5` | `yes` | `factor_comun_incompleto` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E5` | `wrong` | `suma_de_cuadrados_es_factorizable` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E5` | `err` | `confunde_diferencia_con_cuadrado_perfecto` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E6` | `true` | `suma_de_cuadrados_es_factorizable` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E6` | `true_pos` | `suma_de_cuadrados_es_factorizable` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-E6` | `false_never` | `cree_que_dos_terminos_nunca_se_factorizan` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-Q2` | `dif` | `suma_de_cuadrados_es_factorizable` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |
| `ALG-N3-G02-CUADRADOS-Q2` | `tcp` | `no_verifica_el_doble_producto` | Mira tres cosas: cuántos términos hay, si son cuadrados exactos y qué signo llevan. Con eso se decide sin estampar nada. |

### A13. Notas de citas

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Ver `Implementacion/Fase_2/CITAS_EN_REMOJO.md`.

### A14. Notas de handoff a Design

> **PENDIENTE — se escribe a mano.** No es derivable del código.

Imagen de apertura declarada: `— falta`

Renderer: `frontend/src/pages/Student/lessons/blocks/ElevenBlockLesson.tsx` (genérico, 5 zonas de color).
